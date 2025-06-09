#!/bin/bash

# Amsterdam Events Feed - Local WordPress Setup
echo "🇳🇱 Setting up Local WordPress for Amsterdam Events Feed Testing"
echo "================================================================"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop and try again."
    exit 1
fi

echo "✅ Docker is running"

# Check if Docker Compose is available
if ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose not found. Please install Docker Compose."
    exit 1
fi

echo "✅ Docker Compose is available"

# Create custom themes directory
mkdir -p wp-content-custom

# Start the WordPress environment
echo ""
echo "🚀 Starting WordPress environment..."
docker compose up -d

# Wait for services to be ready
echo ""
echo "⏳ Waiting for WordPress to be ready..."
sleep 10

# Check if WordPress is responding
echo "🔍 Checking WordPress status..."
for i in {1..10}; do
    if curl -s http://localhost:8080 > /dev/null; then
        echo "✅ WordPress is ready!"
        break
    else
        echo "   Waiting... (attempt $i/10)"
        sleep 5
    fi
done

echo ""
echo "🎉 Local WordPress Environment is Ready!"
echo "========================================"
echo ""
echo "📱 WordPress Site:     http://localhost:8080"
echo "🗄️  phpMyAdmin:        http://localhost:8081"
echo ""
echo "🔑 Database Credentials:"
echo "   Host:     localhost:3306"
echo "   Database: wordpress"
echo "   User:     wordpress"
echo "   Password: wordpress_password"
echo ""
echo "📋 Next Steps:"
echo "1. Open http://localhost:8080 in your browser"
echo "2. Complete WordPress setup (choose admin credentials)"
echo "3. Install 'Feedzy RSS Feeds' plugin"
echo "4. Add the Amsterdam Events RSS feed:"
echo "   https://raw.githubusercontent.com/lassebenni/amsterdam-events-feed/master/events.xml"
echo ""
echo "🛑 To stop: docker compose down"
echo "🗑️  To remove: docker compose down -v (removes data)"

# Open browser automatically (macOS)
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo ""
    echo "🌐 Opening WordPress in your browser..."
    open http://localhost:8080
fi 