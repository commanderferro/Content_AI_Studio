from fastapi import Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
import time
import hashlib

class SecurityMiddleware:
    def __init__(self, app):
        self.app = app
        
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
            
        request = Request(scope, receive)
        
        # Rate limiting básico
        client_ip = request.client.host
        request_time = time.time()
        
        # Headers de seguridad
        response = await self.app(scope, receive, send)
        
        # Añadir headers de seguridad a la respuesta
        if scope["type"] == "http.response.start":
            headers = dict(scope.get("headers", []))
            headers.extend([
                (b"X-Content-Type-Options", b"nosniff"),
                (b"X-Frame-Options", b"DENY"),
                (b"X-XSS-Protection", b"1; mode=block"),
                (b"Strict-Transport-Security", b"max-age=31536000; includeSubDomains"),
                (b"Content-Security-Policy", b"default-src 'self'"),
                (b"Referrer-Policy", b"strict-origin-when-cross-origin"),
            ])
            scope["headers"] = headers
        
        return response

def setup_security_middleware(app):
    # CORS restringido
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["https://tudominio.com"],  # Solo tu dominio
        allow_credentials=True,
        allow_methods=["GET", "POST"],
        allow_headers=["Authorization", "Content-Type"],
        max_age=3600,
    )
    
    # Solo hosts confiables
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["tudominio.com", "localhost"]
    )
    
    # Compresión
    app.add_middleware(GZipMiddleware, minimum_size=1000)
