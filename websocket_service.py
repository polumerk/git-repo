#!/usr/bin/env python3
"""
WebSocket сервис для real-time коммуникации
"""

import json
import time
import asyncio
import uuid
from typing import Dict, Set, List, Any, Optional
from dataclasses import dataclass, asdict
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    import websockets
    from websockets.server import WebSocketServerProtocol
    WEBSOCKETS_AVAILABLE = True
except ImportError:
    WEBSOCKETS_AVAILABLE = False
    logger.warning("websockets не установлен. WebSocket функциональность недоступна.")

try:
    from ai_chatbot import language_bot
    AI_BOT_AVAILABLE = True
except ImportError:
    AI_BOT_AVAILABLE = False
    logger.warning("AI чат-бот недоступен")

@dataclass
class WebSocketMessage:
    """Структура WebSocket сообщения"""
    type: str  # 'chat', 'typing', 'status', 'error', 'system'
    data: Dict[str, Any]
    timestamp: float
    user_id: Optional[str] = None
    session_id: Optional[str] = None

@dataclass
class ConnectedUser:
    """Информация о подключенном пользователе"""
    user_id: str
    websocket: Any  # WebSocketServerProtocol
    connected_at: float
    last_activity: float
    language_session: Optional[str] = None
    is_typing: bool = False

class WebSocketManager:
    """Менеджер WebSocket соединений"""
    
    def __init__(self):
        self.connected_users: Dict[str, ConnectedUser] = {}
        self.user_sessions: Dict[str, str] = {}  # user_id -> session_id
        self.active_chats: Dict[str, Set[str]] = {}  # chat_room -> set of user_ids
        self.message_history: Dict[str, List[WebSocketMessage]] = {}
        
    async def register_user(self, websocket: Any, user_id: str) -> str:
        """Регистрация нового пользователя"""
        session_id = str(uuid.uuid4())
        
        user = ConnectedUser(
            user_id=user_id,
            websocket=websocket,
            connected_at=time.time(),
            last_activity=time.time()
        )
        
        self.connected_users[user_id] = user
        self.user_sessions[user_id] = session_id
        
        logger.info(f"Пользователь {user_id} подключился (сессия: {session_id})")
        
        # Отправляем приветствие
        await self.send_to_user(user_id, {
            'type': 'system',
            'data': {
                'message': 'Добро пожаловать! Вы подключены к real-time чату.',
                'session_id': session_id,
                'features': ['ai_chat', 'language_learning', 'real_time_updates']
            }
        })
        
        return session_id
    
    async def unregister_user(self, user_id: str):
        """Отключение пользователя"""
        if user_id in self.connected_users:
            user = self.connected_users[user_id]
            
            # Уведомляем других пользователей
            await self.broadcast_user_status(user_id, 'disconnected')
            
            # Удаляем из всех чатов
            for chat_room, users in self.active_chats.items():
                users.discard(user_id)
            
            del self.connected_users[user_id]
            if user_id in self.user_sessions:
                del self.user_sessions[user_id]
            
            logger.info(f"Пользователь {user_id} отключился")
    
    async def send_to_user(self, user_id: str, message_data: Dict[str, Any]):
        """Отправить сообщение конкретному пользователю"""
        if user_id not in self.connected_users:
            logger.warning(f"Пользователь {user_id} не найден")
            return False
        
        user = self.connected_users[user_id]
        message = WebSocketMessage(
            type=message_data.get('type', 'message'),
            data=message_data.get('data', {}),
            timestamp=time.time(),
            user_id=user_id,
            session_id=self.user_sessions.get(user_id)
        )
        
        try:
            await user.websocket.send(json.dumps(asdict(message)))
            user.last_activity = time.time()
            return True
        except Exception as e:
            logger.error(f"Ошибка отправки сообщения пользователю {user_id}: {e}")
            await self.unregister_user(user_id)
            return False
    
    async def broadcast_to_chat(self, chat_room: str, message_data: Dict[str, Any], 
                              exclude_user: Optional[str] = None):
        """Транслировать сообщение всем пользователям в чате"""
        if chat_room not in self.active_chats:
            return
        
        users = self.active_chats[chat_room].copy()
        if exclude_user:
            users.discard(exclude_user)
        
        tasks = []
        for user_id in users:
            tasks.append(self.send_to_user(user_id, message_data))
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def broadcast_user_status(self, user_id: str, status: str):
        """Транслировать статус пользователя"""
        message_data = {
            'type': 'user_status',
            'data': {
                'user_id': user_id,
                'status': status,
                'timestamp': time.time()
            }
        }
        
        # Отправляем всем подключенным пользователям
        tasks = []
        for other_user_id in self.connected_users.keys():
            if other_user_id != user_id:
                tasks.append(self.send_to_user(other_user_id, message_data))
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def join_chat_room(self, user_id: str, chat_room: str):
        """Присоединиться к чат-комнате"""
        if chat_room not in self.active_chats:
            self.active_chats[chat_room] = set()
        
        self.active_chats[chat_room].add(user_id)
        
        # Уведомляем остальных участников
        await self.broadcast_to_chat(chat_room, {
            'type': 'user_joined',
            'data': {
                'user_id': user_id,
                'chat_room': chat_room,
                'timestamp': time.time()
            }
        }, exclude_user=user_id)
        
        # Отправляем пользователю информацию о чате
        await self.send_to_user(user_id, {
            'type': 'chat_joined',
            'data': {
                'chat_room': chat_room,
                'participants': list(self.active_chats[chat_room]),
                'message': f'Вы присоединились к чату "{chat_room}"'
            }
        })
    
    async def leave_chat_room(self, user_id: str, chat_room: str):
        """Покинуть чат-комнату"""
        if chat_room in self.active_chats:
            self.active_chats[chat_room].discard(user_id)
            
            # Уведомляем остальных участников
            await self.broadcast_to_chat(chat_room, {
                'type': 'user_left',
                'data': {
                    'user_id': user_id,
                    'chat_room': chat_room,
                    'timestamp': time.time()
                }
            })
            
            # Удаляем пустые чаты
            if not self.active_chats[chat_room]:
                del self.active_chats[chat_room]
    
    async def handle_chat_message(self, user_id: str, message: str, chat_room: str = 'general'):
        """Обработать чат-сообщение"""
        
        # Добавляем в историю
        if chat_room not in self.message_history:
            self.message_history[chat_room] = []
        
        chat_msg = WebSocketMessage(
            type='chat',
            data={
                'user_id': user_id,
                'message': message,
                'chat_room': chat_room
            },
            timestamp=time.time(),
            user_id=user_id
        )
        
        self.message_history[chat_room].append(chat_msg)
        
        # Ограничиваем историю (последние 100 сообщений)
        if len(self.message_history[chat_room]) > 100:
            self.message_history[chat_room] = self.message_history[chat_room][-100:]
        
        # Транслируем сообщение
        await self.broadcast_to_chat(chat_room, {
            'type': 'chat_message',
            'data': {
                'user_id': user_id,
                'message': message,
                'timestamp': time.time(),
                'chat_room': chat_room
            }
        })
    
    async def handle_ai_chat(self, user_id: str, message: str, target_language: str = 'ru', 
                           level: str = 'beginner'):
        """Обработать сообщение для AI чат-бота"""
        if not AI_BOT_AVAILABLE:
            await self.send_to_user(user_id, {
                'type': 'error',
                'data': {'message': 'AI чат-бот недоступен'}
            })
            return
        
        try:
            # Создаем или получаем сессию обучения
            session_key = f"{user_id}_{target_language}"
            if session_key not in language_bot.sessions:
                language_bot.create_learning_session(session_key, target_language, 'ru', level)
            
            # Отправляем индикатор набора текста
            await self.send_to_user(user_id, {
                'type': 'ai_typing',
                'data': {'is_typing': True}
            })
            
            # Обрабатываем сообщение через AI бота
            response = language_bot.process_message(session_key, message)
            
            # Убираем индикатор набора текста
            await self.send_to_user(user_id, {
                'type': 'ai_typing',
                'data': {'is_typing': False}
            })
            
            # Отправляем ответ
            await self.send_to_user(user_id, {
                'type': 'ai_response',
                'data': {
                    'user_message': message,
                    'bot_response': response.get('response', ''),
                    'suggestions': response.get('suggestions', []),
                    'corrections': response.get('corrections', []),
                    'progress_score': response.get('progress_score', 0),
                    'confidence': response.get('confidence', 0.8),
                    'timestamp': time.time()
                }
            })
            
        except Exception as e:
            logger.error(f"Ошибка AI чата: {e}")
            await self.send_to_user(user_id, {
                'type': 'error',
                'data': {'message': f'Ошибка AI чата: {str(e)}'}
            })
    
    async def handle_typing_indicator(self, user_id: str, is_typing: bool, chat_room: str = 'general'):
        """Обработать индикатор набора текста"""
        if user_id in self.connected_users:
            self.connected_users[user_id].is_typing = is_typing
        
        # Транслируем статус набора
        await self.broadcast_to_chat(chat_room, {
            'type': 'typing_indicator',
            'data': {
                'user_id': user_id,
                'is_typing': is_typing,
                'timestamp': time.time()
            }
        }, exclude_user=user_id)
    
    async def get_chat_history(self, user_id: str, chat_room: str, limit: int = 50):
        """Получить историю чата"""
        history = self.message_history.get(chat_room, [])
        recent_history = history[-limit:] if len(history) > limit else history
        
        await self.send_to_user(user_id, {
            'type': 'chat_history',
            'data': {
                'chat_room': chat_room,
                'messages': [asdict(msg) for msg in recent_history],
                'total_messages': len(history)
            }
        })
    
    async def get_online_users(self, user_id: str):
        """Получить список онлайн пользователей"""
        online_users = []
        current_time = time.time()
        
        for uid, user in self.connected_users.items():
            online_users.append({
                'user_id': uid,
                'connected_at': user.connected_at,
                'last_activity': user.last_activity,
                'is_typing': user.is_typing,
                'session_duration': current_time - user.connected_at
            })
        
        await self.send_to_user(user_id, {
            'type': 'online_users',
            'data': {
                'users': online_users,
                'total_online': len(online_users)
            }
        })
    
    async def cleanup_inactive_users(self, max_inactive_minutes: int = 30):
        """Очистка неактивных пользователей"""
        current_time = time.time()
        cutoff_time = current_time - (max_inactive_minutes * 60)
        
        inactive_users = [
            user_id for user_id, user in self.connected_users.items()
            if user.last_activity < cutoff_time
        ]
        
        for user_id in inactive_users:
            await self.unregister_user(user_id)
        
        return len(inactive_users)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Получить статистику WebSocket соединений"""
        current_time = time.time()
        
        total_messages = sum(len(history) for history in self.message_history.values())
        
        user_stats = []
        for user_id, user in self.connected_users.items():
            user_stats.append({
                'user_id': user_id,
                'session_duration': current_time - user.connected_at,
                'last_activity_ago': current_time - user.last_activity,
                'is_typing': user.is_typing
            })
        
        return {
            'connected_users': len(self.connected_users),
            'active_chats': len(self.active_chats),
            'total_messages': total_messages,
            'user_stats': user_stats,
            'chat_rooms': list(self.active_chats.keys()),
            'uptime': current_time,
            'websockets_available': WEBSOCKETS_AVAILABLE,
            'ai_bot_available': AI_BOT_AVAILABLE
        }


# Глобальный менеджер WebSocket
websocket_manager = WebSocketManager()


async def websocket_handler(websocket: Any, path: str):
    """Основной обработчик WebSocket соединений"""
    user_id = None
    
    try:
        # Ожидаем первое сообщение с идентификацией пользователя
        auth_message = await websocket.recv()
        auth_data = json.loads(auth_message)
        
        if auth_data.get('type') != 'auth':
            await websocket.send(json.dumps({
                'type': 'error',
                'data': {'message': 'Требуется аутентификация'}
            }))
            return
        
        user_id = auth_data.get('user_id', f'user_{int(time.time())}')
        
        # Регистрируем пользователя
        session_id = await websocket_manager.register_user(websocket, user_id)
        
        # Основной цикл обработки сообщений
        async for message_raw in websocket:
            try:
                message_data = json.loads(message_raw)
                message_type = message_data.get('type')
                data = message_data.get('data', {})
                
                if message_type == 'chat':
                    await websocket_manager.handle_chat_message(
                        user_id, 
                        data.get('message', ''),
                        data.get('chat_room', 'general')
                    )
                
                elif message_type == 'ai_chat':
                    await websocket_manager.handle_ai_chat(
                        user_id,
                        data.get('message', ''),
                        data.get('target_language', 'ru'),
                        data.get('level', 'beginner')
                    )
                
                elif message_type == 'typing':
                    await websocket_manager.handle_typing_indicator(
                        user_id,
                        data.get('is_typing', False),
                        data.get('chat_room', 'general')
                    )
                
                elif message_type == 'join_chat':
                    await websocket_manager.join_chat_room(
                        user_id,
                        data.get('chat_room', 'general')
                    )
                
                elif message_type == 'leave_chat':
                    await websocket_manager.leave_chat_room(
                        user_id,
                        data.get('chat_room', 'general')
                    )
                
                elif message_type == 'get_history':
                    await websocket_manager.get_chat_history(
                        user_id,
                        data.get('chat_room', 'general'),
                        data.get('limit', 50)
                    )
                
                elif message_type == 'get_online':
                    await websocket_manager.get_online_users(user_id)
                
                else:
                    await websocket_manager.send_to_user(user_id, {
                        'type': 'error',
                        'data': {'message': f'Неизвестный тип сообщения: {message_type}'}
                    })
                    
            except json.JSONDecodeError:
                await websocket_manager.send_to_user(user_id, {
                    'type': 'error',
                    'data': {'message': 'Неверный формат JSON'}
                })
            except Exception as e:
                logger.error(f"Ошибка обработки сообщения: {e}")
                await websocket_manager.send_to_user(user_id, {
                    'type': 'error',
                    'data': {'message': f'Ошибка сервера: {str(e)}'}
                })
                
    except Exception as e:
        logger.error(f"Ошибка WebSocket соединения: {e}")
    finally:
        if user_id:
            await websocket_manager.unregister_user(user_id)


def start_websocket_server(host: str = '0.0.0.0', port: int = 8765):
    """Запустить WebSocket сервер"""
    if not WEBSOCKETS_AVAILABLE:
        logger.error("websockets библиотека не установлена")
        return None
    
    logger.info(f"Запуск WebSocket сервера на {host}:{port}")
    
    return websockets.serve(websocket_handler, host, port)


if __name__ == '__main__':
    # Тестирование WebSocket сервиса
    print("⚡ Тестирование WebSocket сервиса...")
    
    if not WEBSOCKETS_AVAILABLE:
        print("❌ websockets не установлен. Установите: pip install websockets")
    else:
        print("✅ websockets доступен")
    
    if not AI_BOT_AVAILABLE:
        print("❌ AI чат-бот недоступен")
    else:
        print("✅ AI чат-бот подключен")
    
    # Тестируем менеджер
    manager = WebSocketManager()
    stats = manager.get_statistics()
    
    print(f"\n📊 Статистика WebSocket:")
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    print("\n🚀 Для запуска WebSocket сервера:")
    print("   python3 websocket_service.py")
    print("   Подключение: ws://localhost:8765")
    
    if WEBSOCKETS_AVAILABLE:
        print("\n🔄 Запуск WebSocket сервера...")
        print("Нажмите Ctrl+C для остановки")
        
        try:
            # Запускаем сервер
            server = start_websocket_server()
            if server:
                asyncio.get_event_loop().run_until_complete(server)
                asyncio.get_event_loop().run_forever()
        except KeyboardInterrupt:
            print("\n👋 WebSocket сервер остановлен")
    
    print("✅ Тестирование завершено!")