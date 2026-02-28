#!/bin/bash
# SEGURIDAD AVANZADA PARA CONTENT AI v4.3

set -e
echo "🛡️  CONFIGURACIÓN DE SEGURIDAD AVANZADA"
echo "========================================"

# Verificar que estamos como root o con sudo
if [ "$EUID" -ne 0 ]; then 
    echo "⚠️  Ejecuta con sudo: sudo ./enhanced-security.sh"
    exit 1
fi

# 1. CONFIGURACIÓN DE RED Y FIREWALL
echo "🔥 Configurando reglas de firewall avanzadas..."
ufw --force reset

# Solo puertos esenciales
ufw allow 22/tcp comment 'SSH'
ufw allow 443/tcp comment 'HTTPS'
ufw allow 80/tcp comment 'HTTP redirection'
ufw default deny incoming
ufw default allow outgoing
ufw --force enable

# Reglas específicas para Docker
iptables -I DOCKER-USER -i eth0 -p tcp --dport 7474 -j DROP 2>/dev/null || true
iptables -I DOCKER-USER -i eth0 -p tcp --dport 7687 -j DROP 2>/dev/null || true

# 2. HARDENING DE DOCKER
echo "🐳 Aplicando hardening a Docker..."
cat > /etc/docker/daemon.json << DOCKEREOF
{
  "userns-remap": "default",
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  },
  "live-restore": true,
  "userland-proxy": false,
  "no-new-privileges": true
}
DOCKEREOF

# 3. CONFIGURACIÓN DE SSL/TLS AUTOMÁTICA
echo "🔐 Configurando SSL con Let's Encrypt..."
mkdir -p nginx/ssl
cat > nginx/nginx-secure.conf << NGINXEOF
events {
    worker_connections 1024;
}

http {
    # Redirección HTTP → HTTPS
    server {
        listen 80;
        server_name tudominio.com;
        return 301 https://\$server_name\$request_uri;
    }

    # Servidor HTTPS
    server {
        listen 443 ssl http2;
        server_name tudominio.com;

        ssl_certificate /etc/nginx/ssl/fullchain.pem;
        ssl_certificate_key /etc/nginx/ssl/privkey.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
        ssl_prefer_server_ciphers off;
        ssl_session_cache shared:SSL:10m;

        # Headers de seguridad
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";
        add_header Strict-Transport-Security "max-age=63072000" always;

        # Proxy a Dashboard
        location / {
            proxy_pass http://dashboard:8501;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
            
            # Protección dashboard
            auth_basic "Content AI Dashboard";
            auth_basic_user_file /etc/nginx/.htpasswd;
        }

        # Proxy a API
        location /api/ {
            proxy_pass http://backend:8000;
            proxy_set_header Host \$host;
            
            # Rate limiting
            limit_req zone=api burst=10 nodelay;
        }
    }

    # Zona para rate limiting
    limit_req_zone \$binary_remote_addr zone=api:10m rate=1r/s;
}
NGINXEOF

# 4. CONTRASEÑAS Y API KEYS MEJORADAS
echo "🔑 Generando credenciales ultra-seguras..."
generate_ultra_secure() {
    cat /dev/urandom | tr -dc 'a-zA-Z0-9!@#$%^&*()_+-=' | fold -w 32 | head -n 1
}

# Actualizar .env con credenciales seguras
if [ -f .env ]; then
    # Backup del .env original
    cp .env .env.backup.$(date +%s)

    # Generar nuevas credenciales
    NEW_API_KEY=$(openssl rand -hex 32)
    NEW_DASH_PASS=$(generate_ultra_secure)
    NEW_NEO4J_PASS=$(openssl rand -base64 32 | tr -d '/+=' | head -c 40)
    NEW_POSTGRES_PASS=$(openssl rand -base64 32 | tr -d '/+=' | head -c 40)

    # Actualizar .env
    sed -i "s|API_KEY=.*|API_KEY=$NEW_API_KEY|" .env
    sed -i "s|DASHBOARD_PASSWORD=.*|DASHBOARD_PASSWORD=$NEW_DASH_PASS|" .env
    sed -i "s|NEO4J_PASSWORD=.*|NEO4J_PASSWORD=$NEW_NEO4J_PASS|" .env
    sed -i "s|POSTGRES_PASSWORD=.*|POSTGRES_PASSWORD=$NEW_POSTGRES_PASS|" .env

    echo "✅ Credenciales actualizadas"
    echo ""
    echo "📋 NUEVAS CREDENCIALES (GUÁRDALAS):"
    echo "====================================="
    echo "🔐 API Key: $NEW_API_KEY"
    echo "📊 Dashboard Password: $NEW_DASH_PASS"
    echo "🗄️  Neo4j Password: $NEW_NEO4J_PASS"
    echo "💾 PostgreSQL Password: $NEW_POSTGRES_PASS"
    echo "====================================="
    echo "⚠️  Estas credenciales NO se volverán a mostrar"
else
    echo "❌ No se encontró archivo .env"
fi

# 5. CONFIGURAR FAIL2BAN
echo "🚨 Configurando Fail2Ban..."
apt-get install -y fail2ban

cat > /etc/fail2ban/jail.d/content-ai.conf << FAIL2BANEOF
[content-ai-api]
enabled = true
port = 8000,8501
filter = content-ai
logpath = /var/log/docker-compose.log
maxretry = 3
bantime = 3600

[nginx-http-auth]
enabled = true
port = http,https
filter = nginx
logpath = /var/log/nginx/error.log
maxretry = 3
bantime = 3600
FAIL2BANEOF

# 6. AUDITORÍA Y LOGS
echo "📊 Configurando auditoría..."
cat > /etc/audit/rules.d/content-ai.rules << AUDITEOF
-w /etc/docker/daemon.json -p wa -k docker_config
-w /var/lib/docker -p wa -k docker_data
-w /root/content-ai-complete/.env -p wa -k env_file
-w /root/content-ai-complete/docker-compose.yml -p wa -k docker_compose
AUDITEOF

# 7. MONITOREO DE INTEGRIDAD
echo "🔍 Configurando monitoreo de integridad..."
apt-get install -y aide
aideinit
cp /var/lib/aide/aide.db.new /var/lib/aide/aide.db

# 8. SCRIPT DE RESPALDO ENCRIPTADO
cat > encrypted-backup.sh << 'EOF'
#!/bin/bash
# BACKUP ENCRIPTADO DE CONTENT AI

BACKUP_DIR="/backup/content-ai/$(date +%Y%m%d_%H%M%S)"
ENCRYPTION_KEY="/root/.backup_key"
mkdir -p $BACKUP_DIR

echo "🔐 Creando backup encriptado..."

# Generar clave de encriptación si no existe
if [ ! -f "$ENCRYPTION_KEY" ]; then
    openssl rand -base64 256 > $ENCRYPTION_KEY
    chmod 400 $ENCRYPTION_KEY
fi

# Backup de datos sensibles
docker-compose exec -T postgres pg_dump -U contentai contentai | gzip > $BACKUP_DIR/postgres.sql.gz
docker-compose exec -T neo4j neo4j-admin dump --database=neo4j --to=/backup/neo4j.dump
docker cp content-ai-complete_neo4j_1:/backup/neo4j.dump $BACKUP_DIR/

# Comprimir y encriptar
tar -czf - $BACKUP_DIR | openssl enc -aes-256-cbc -salt -pass file:$ENCRYPTION_KEY -out $BACKUP_DIR.tar.gz.enc

# Subir a S3/Cloud (opcional)
# aws s3 cp $BACKUP_DIR.tar.gz.enc s3://tu-bucket/backups/

echo "✅ Backup encriptado creado: $BACKUP_DIR.tar.gz.enc"
echo "🔑 Clave de encriptación guardada en: $ENCRYPTION_KEY"
