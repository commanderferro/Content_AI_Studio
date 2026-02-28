#!/bin/bash
# VERIFICACIÓN DE SEGURIDAD DIARIA

echo "🔍 VERIFICACIÓN DE SEGURIDAD - $(date)"
echo "======================================"

# 1. Verificar puertos expuestos
echo "📡 Puertos abiertos:"
ss -tulpn | grep LISTEN

# 2. Verificar contenedores
echo "🐳 Estado de contenedores:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# 3. Verificar logs de seguridad
echo "📋 Logs de seguridad recientes:"
journalctl -u docker --since "24 hours ago" | grep -i "error\|fail\|auth" | tail -20

# 4. Verificar actualizaciones de seguridad
echo "🔄 Actualizaciones disponibles:"
apt list --upgradable 2>/dev/null | grep security || echo "✅ Sin actualizaciones de seguridad pendientes"

# 5. Verificar uso de recursos
echo "💾 Uso de recursos:"
free -h && echo "---" && df -h /

# 6. Verificar certificados SSL
echo "🔐 Certificados SSL:"
if [ -f "nginx/ssl/fullchain.pem" ]; then
    openssl x509 -in nginx/ssl/fullchain.pem -text -noout | grep -A2 "Validity"
else
    echo "⚠️  No se encontraron certificados SSL"
fi

# 7. Verificar backups
echo "💿 Backups recientes:"
find ./backups -name "*.tar.gz" -mtime -7 2>/dev/null | wc -l | xargs echo "Backups últimos 7 días:"

echo ""
echo "✅ Verificación completada"
