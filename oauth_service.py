#!/usr/bin/env python3
"""
OAuth сервис аутентификации
"""

import os
import json
import time
import secrets
import hashlib
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from urllib.parse import urlencode, parse_qs
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    logger.warning("requests не установлен")

try:
    import jwt
    JWT_AVAILABLE = True
except ImportError:
    JWT_AVAILABLE = False
    logger.warning("PyJWT не установлен")

try:
    from database import get_database_connection
    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False
    logger.warning("Database недоступна")

@dataclass
class OAuthProvider:
    """Конфигурация OAuth провайдера"""
    name: str
    client_id: str
    client_secret: str
    auth_url: str
    token_url: str
    user_info_url: str
    scope: str
    redirect_uri: str

@dataclass
class UserProfile:
    """Профиль пользователя"""
    user_id: str
    provider: str
    email: str
    name: str
    avatar_url: Optional[str] = None
    locale: Optional[str] = None
    verified: bool = False
    created_at: float = 0.0
    last_login: float = 0.0
    additional_data: Dict[str, Any] = None

@dataclass
class AuthSession:
    """Сессия аутентификации"""
    session_id: str
    user_id: str
    access_token: str
    refresh_token: Optional[str]
    expires_at: float
    created_at: float
    provider: str
    scope: List[str]

class OAuthService:
    """Сервис OAuth аутентификации"""
    
    def __init__(self):
        self.providers: Dict[str, OAuthProvider] = {}
        self.sessions: Dict[str, AuthSession] = {}
        self.users: Dict[str, UserProfile] = {}
        self.pending_auth: Dict[str, Dict[str, Any]] = {}  # state -> auth data
        
        # JWT секрет
        self.jwt_secret = os.getenv('JWT_SECRET', self._generate_jwt_secret())
        
        self._setup_providers()
        self._load_users_from_database()
    
    def _generate_jwt_secret(self) -> str:
        """Генерировать JWT секрет"""
        return secrets.token_urlsafe(32)
    
    def _setup_providers(self):
        """Настройка OAuth провайдеров"""
        
        # Google OAuth
        google_client_id = os.getenv('GOOGLE_CLIENT_ID')
        google_client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
        
        if google_client_id and google_client_secret:
            self.providers['google'] = OAuthProvider(
                name='google',
                client_id=google_client_id,
                client_secret=google_client_secret,
                auth_url='https://accounts.google.com/o/oauth2/v2/auth',
                token_url='https://oauth2.googleapis.com/token',
                user_info_url='https://www.googleapis.com/oauth2/v2/userinfo',
                scope='openid email profile',
                redirect_uri=os.getenv('GOOGLE_REDIRECT_URI', 'http://localhost:5000/auth/google/callback')
            )
            logger.info("Google OAuth настроен")
        else:
            logger.warning("Google OAuth не настроен (отсутствуют GOOGLE_CLIENT_ID/GOOGLE_CLIENT_SECRET)")
        
        # GitHub OAuth
        github_client_id = os.getenv('GITHUB_CLIENT_ID')
        github_client_secret = os.getenv('GITHUB_CLIENT_SECRET')
        
        if github_client_id and github_client_secret:
            self.providers['github'] = OAuthProvider(
                name='github',
                client_id=github_client_id,
                client_secret=github_client_secret,
                auth_url='https://github.com/login/oauth/authorize',
                token_url='https://github.com/login/oauth/access_token',
                user_info_url='https://api.github.com/user',
                scope='user:email',
                redirect_uri=os.getenv('GITHUB_REDIRECT_URI', 'http://localhost:5000/auth/github/callback')
            )
            logger.info("GitHub OAuth настроен")
        else:
            logger.warning("GitHub OAuth не настроен (отсутствуют GITHUB_CLIENT_ID/GITHUB_CLIENT_SECRET)")
        
        # VK OAuth
        vk_client_id = os.getenv('VK_CLIENT_ID')
        vk_client_secret = os.getenv('VK_CLIENT_SECRET')
        
        if vk_client_id and vk_client_secret:
            self.providers['vk'] = OAuthProvider(
                name='vk',
                client_id=vk_client_id,
                client_secret=vk_client_secret,
                auth_url='https://oauth.vk.com/authorize',
                token_url='https://oauth.vk.com/access_token',
                user_info_url='https://api.vk.com/method/users.get',
                scope='email',
                redirect_uri=os.getenv('VK_REDIRECT_URI', 'http://localhost:5000/auth/vk/callback')
            )
            logger.info("VK OAuth настроен")
        else:
            logger.warning("VK OAuth не настроен (отсутствуют VK_CLIENT_ID/VK_CLIENT_SECRET)")
    
    def _load_users_from_database(self):
        """Загрузить пользователей из базы данных"""
        if not DATABASE_AVAILABLE:
            return
        
        try:
            conn = get_database_connection()
            cursor = conn.cursor()
            
            # Создаем таблицу пользователей если не существует
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS oauth_users (
                    user_id TEXT PRIMARY KEY,
                    provider TEXT NOT NULL,
                    email TEXT NOT NULL,
                    name TEXT NOT NULL,
                    avatar_url TEXT,
                    locale TEXT,
                    verified BOOLEAN DEFAULT FALSE,
                    created_at REAL NOT NULL,
                    last_login REAL NOT NULL,
                    additional_data TEXT
                )
            ''')
            
            # Загружаем пользователей
            cursor.execute('SELECT * FROM oauth_users')
            for row in cursor.fetchall():
                user_data = dict(row)
                additional_data = json.loads(user_data.get('additional_data', '{}'))
                
                user = UserProfile(
                    user_id=user_data['user_id'],
                    provider=user_data['provider'],
                    email=user_data['email'],
                    name=user_data['name'],
                    avatar_url=user_data.get('avatar_url'),
                    locale=user_data.get('locale'),
                    verified=bool(user_data.get('verified', False)),
                    created_at=user_data['created_at'],
                    last_login=user_data['last_login'],
                    additional_data=additional_data
                )
                
                self.users[user.user_id] = user
            
            conn.close()
            logger.info(f"Загружено {len(self.users)} пользователей из базы данных")
            
        except Exception as e:
            logger.error(f"Ошибка загрузки пользователей: {e}")
    
    def _save_user_to_database(self, user: UserProfile):
        """Сохранить пользователя в базу данных"""
        if not DATABASE_AVAILABLE:
            return
        
        try:
            conn = get_database_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO oauth_users 
                (user_id, provider, email, name, avatar_url, locale, verified, created_at, last_login, additional_data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user.user_id,
                user.provider,
                user.email,
                user.name,
                user.avatar_url,
                user.locale,
                user.verified,
                user.created_at,
                user.last_login,
                json.dumps(user.additional_data or {})
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Ошибка сохранения пользователя: {e}")
    
    def get_auth_url(self, provider_name: str) -> Dict[str, Any]:
        """Получить URL для авторизации"""
        if provider_name not in self.providers:
            return {'error': f'Провайдер {provider_name} не поддерживается'}
        
        provider = self.providers[provider_name]
        
        # Генерируем state для защиты от CSRF
        state = secrets.token_urlsafe(32)
        
        # Сохраняем состояние авторизации
        self.pending_auth[state] = {
            'provider': provider_name,
            'created_at': time.time(),
            'redirect_uri': provider.redirect_uri
        }
        
        # Формируем параметры авторизации
        auth_params = {
            'client_id': provider.client_id,
            'redirect_uri': provider.redirect_uri,
            'scope': provider.scope,
            'response_type': 'code',
            'state': state
        }
        
        # Специальные параметры для разных провайдеров
        if provider_name == 'google':
            auth_params['access_type'] = 'offline'
            auth_params['prompt'] = 'consent'
        
        auth_url = f"{provider.auth_url}?{urlencode(auth_params)}"
        
        return {
            'auth_url': auth_url,
            'state': state,
            'provider': provider_name
        }
    
    def handle_callback(self, provider_name: str, code: str, state: str) -> Dict[str, Any]:
        """Обработать callback от OAuth провайдера"""
        
        # Проверяем state
        if state not in self.pending_auth:
            return {'error': 'Invalid state parameter'}
        
        auth_data = self.pending_auth[state]
        if auth_data['provider'] != provider_name:
            return {'error': 'Provider mismatch'}
        
        # Удаляем использованный state
        del self.pending_auth[state]
        
        if provider_name not in self.providers:
            return {'error': f'Provider {provider_name} not supported'}
        
        provider = self.providers[provider_name]
        
        try:
            # Обмениваем код на токен
            token_data = self._exchange_code_for_token(provider, code)
            if 'error' in token_data:
                return token_data
            
            # Получаем информацию о пользователе
            user_info = self._get_user_info(provider, token_data['access_token'])
            if 'error' in user_info:
                return user_info
            
            # Создаем или обновляем профиль пользователя
            user_profile = self._create_or_update_user_profile(provider_name, user_info, token_data)
            
            # Создаем сессию
            session = self._create_auth_session(user_profile, token_data)
            
            # Генерируем JWT токен
            jwt_token = self._generate_jwt_token(user_profile, session)
            
            return {
                'success': True,
                'user': asdict(user_profile),
                'session': asdict(session),
                'jwt_token': jwt_token,
                'expires_in': int(token_data.get('expires_in', 3600))
            }
            
        except Exception as e:
            logger.error(f"Ошибка обработки callback: {e}")
            return {'error': f'Authentication failed: {str(e)}'}
    
    def _exchange_code_for_token(self, provider: OAuthProvider, code: str) -> Dict[str, Any]:
        """Обменять код на токен доступа"""
        if not REQUESTS_AVAILABLE:
            return {'error': 'requests library not available'}
        
        token_params = {
            'client_id': provider.client_id,
            'client_secret': provider.client_secret,
            'code': code,
            'redirect_uri': provider.redirect_uri,
        }
        
        if provider.name == 'github':
            token_params['grant_type'] = 'authorization_code'
            headers = {'Accept': 'application/json'}
        else:
            token_params['grant_type'] = 'authorization_code'
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        
        try:
            response = requests.post(
                provider.token_url,
                data=token_params,
                headers=headers,
                timeout=10
            )
            
            if response.status_code != 200:
                return {'error': f'Token request failed: {response.status_code}'}
            
            if provider.name == 'github':
                token_data = response.json()
            else:
                # Для Google и VK
                token_data = response.json()
            
            if 'access_token' not in token_data:
                return {'error': 'No access token in response'}
            
            return token_data
            
        except requests.RequestException as e:
            return {'error': f'Token request failed: {str(e)}'}
    
    def _get_user_info(self, provider: OAuthProvider, access_token: str) -> Dict[str, Any]:
        """Получить информацию о пользователе"""
        if not REQUESTS_AVAILABLE:
            return {'error': 'requests library not available'}
        
        headers = {'Authorization': f'Bearer {access_token}'}
        
        # Специальные параметры для VK
        if provider.name == 'vk':
            params = {
                'access_token': access_token,
                'v': '5.131',
                'fields': 'email,photo_100'
            }
            url = provider.user_info_url
        else:
            params = {}
            url = provider.user_info_url
        
        try:
            response = requests.get(
                url,
                headers=headers,
                params=params,
                timeout=10
            )
            
            if response.status_code != 200:
                return {'error': f'User info request failed: {response.status_code}'}
            
            user_data = response.json()
            
            # Обработка специфики провайдеров
            if provider.name == 'vk':
                if 'response' in user_data and user_data['response']:
                    return user_data['response'][0]
                else:
                    return {'error': 'VK API error'}
            
            return user_data
            
        except requests.RequestException as e:
            return {'error': f'User info request failed: {str(e)}'}
    
    def _create_or_update_user_profile(self, provider_name: str, user_info: Dict[str, Any], 
                                     token_data: Dict[str, Any]) -> UserProfile:
        """Создать или обновить профиль пользователя"""
        
        # Извлекаем данные в зависимости от провайдера
        if provider_name == 'google':
            user_id = f"google_{user_info['id']}"
            email = user_info.get('email', '')
            name = user_info.get('name', '')
            avatar_url = user_info.get('picture')
            locale = user_info.get('locale')
            verified = user_info.get('verified_email', False)
            
        elif provider_name == 'github':
            user_id = f"github_{user_info['id']}"
            email = user_info.get('email', '')
            name = user_info.get('name') or user_info.get('login', '')
            avatar_url = user_info.get('avatar_url')
            locale = None
            verified = True  # GitHub emails are considered verified
            
        elif provider_name == 'vk':
            user_id = f"vk_{user_info['id']}"
            email = user_info.get('email', '')
            name = f"{user_info.get('first_name', '')} {user_info.get('last_name', '')}".strip()
            avatar_url = user_info.get('photo_100')
            locale = None
            verified = True
            
        else:
            raise ValueError(f"Unknown provider: {provider_name}")
        
        current_time = time.time()
        
        # Создаем или обновляем профиль
        if user_id in self.users:
            user = self.users[user_id]
            user.last_login = current_time
            user.email = email or user.email
            user.name = name or user.name
            user.avatar_url = avatar_url or user.avatar_url
            user.locale = locale or user.locale
            user.verified = verified or user.verified
        else:
            user = UserProfile(
                user_id=user_id,
                provider=provider_name,
                email=email,
                name=name,
                avatar_url=avatar_url,
                locale=locale,
                verified=verified,
                created_at=current_time,
                last_login=current_time,
                additional_data=user_info
            )
        
        self.users[user_id] = user
        self._save_user_to_database(user)
        
        return user
    
    def _create_auth_session(self, user: UserProfile, token_data: Dict[str, Any]) -> AuthSession:
        """Создать сессию аутентификации"""
        session_id = secrets.token_urlsafe(32)
        current_time = time.time()
        
        # Определяем время истечения токена
        expires_in = token_data.get('expires_in', 3600)
        expires_at = current_time + expires_in
        
        session = AuthSession(
            session_id=session_id,
            user_id=user.user_id,
            access_token=token_data['access_token'],
            refresh_token=token_data.get('refresh_token'),
            expires_at=expires_at,
            created_at=current_time,
            provider=user.provider,
            scope=token_data.get('scope', '').split() if token_data.get('scope') else []
        )
        
        self.sessions[session_id] = session
        
        return session
    
    def _generate_jwt_token(self, user: UserProfile, session: AuthSession) -> Optional[str]:
        """Генерировать JWT токен"""
        if not JWT_AVAILABLE:
            logger.warning("JWT не доступен")
            return None
        
        payload = {
            'user_id': user.user_id,
            'session_id': session.session_id,
            'provider': user.provider,
            'email': user.email,
            'name': user.name,
            'iat': int(time.time()),
            'exp': int(session.expires_at)
        }
        
        try:
            token = jwt.encode(payload, self.jwt_secret, algorithm='HS256')
            return token
        except Exception as e:
            logger.error(f"Ошибка создания JWT: {e}")
            return None
    
    def verify_jwt_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Проверить JWT токен"""
        if not JWT_AVAILABLE:
            return None
        
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=['HS256'])
            
            # Проверяем, что сессия еще активна
            session_id = payload.get('session_id')
            if session_id not in self.sessions:
                return None
            
            session = self.sessions[session_id]
            if session.expires_at < time.time():
                # Удаляем истекшую сессию
                del self.sessions[session_id]
                return None
            
            return payload
            
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def logout(self, session_id: str) -> bool:
        """Выйти из системы"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False
    
    def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """Получить профиль пользователя"""
        return self.users.get(user_id)
    
    def get_supported_providers(self) -> List[Dict[str, Any]]:
        """Получить список поддерживаемых провайдеров"""
        providers = []
        for name, provider in self.providers.items():
            providers.append({
                'name': name,
                'display_name': name.title(),
                'available': True,
                'scopes': provider.scope.split()
            })
        
        return providers
    
    def cleanup_expired_sessions(self) -> int:
        """Очистить истекшие сессии"""
        current_time = time.time()
        expired_sessions = [
            session_id for session_id, session in self.sessions.items()
            if session.expires_at < current_time
        ]
        
        for session_id in expired_sessions:
            del self.sessions[session_id]
        
        return len(expired_sessions)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Получить статистику OAuth сервиса"""
        current_time = time.time()
        
        active_sessions = len(self.sessions)
        total_users = len(self.users)
        
        provider_stats = {}
        for provider_name in self.providers.keys():
            provider_users = sum(1 for user in self.users.values() if user.provider == provider_name)
            provider_stats[provider_name] = provider_users
        
        recent_logins = sum(1 for user in self.users.values() 
                          if current_time - user.last_login < 86400)  # последние 24 часа
        
        return {
            'total_users': total_users,
            'active_sessions': active_sessions,
            'supported_providers': len(self.providers),
            'provider_stats': provider_stats,
            'recent_logins_24h': recent_logins,
            'jwt_available': JWT_AVAILABLE,
            'database_available': DATABASE_AVAILABLE,
            'requests_available': REQUESTS_AVAILABLE
        }


# Глобальный экземпляр OAuth сервиса
oauth_service = OAuthService()


if __name__ == '__main__':
    # Тестирование OAuth сервиса
    print("🔐 Тестирование OAuth сервиса...")
    
    service = OAuthService()
    
    # Проверяем доступность компонентов
    print(f"✅ JWT доступен: {JWT_AVAILABLE}")
    print(f"✅ Requests доступен: {REQUESTS_AVAILABLE}")
    print(f"✅ Database доступна: {DATABASE_AVAILABLE}")
    
    # Статистика
    stats = service.get_statistics()
    print(f"\n📊 Статистика OAuth:")
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    # Поддерживаемые провайдеры
    providers = service.get_supported_providers()
    print(f"\n🔗 Поддерживаемые провайдеры: {len(providers)}")
    for provider in providers:
        print(f"   {provider['display_name']}: {provider['available']}")
    
    # Пример использования
    if providers:
        print(f"\n🚀 Пример получения auth URL:")
        provider_name = providers[0]['name']
        auth_data = service.get_auth_url(provider_name)
        
        if 'auth_url' in auth_data:
            print(f"   Провайдер: {provider_name}")
            print(f"   Auth URL: {auth_data['auth_url'][:100]}...")
            print(f"   State: {auth_data['state']}")
        else:
            print(f"   Ошибка: {auth_data.get('error')}")
    
    print("\n✅ Тестирование завершено!")
    print("\n💡 Для настройки OAuth добавьте переменные окружения:")
    print("   export GOOGLE_CLIENT_ID='your_google_client_id'")
    print("   export GOOGLE_CLIENT_SECRET='your_google_client_secret'")
    print("   export GITHUB_CLIENT_ID='your_github_client_id'")
    print("   export GITHUB_CLIENT_SECRET='your_github_client_secret'")