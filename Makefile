# Amsterdam Events Feed - Makefile
# Provides convenient commands for scraping events and managing WordPress

.PHONY: help install scrape feed test wordpress-start wordpress-stop wordpress-restart wordpress-logs wordpress-open wordpress-reset clean status

# Default target
help: ## Show this help message
	@echo "🇳🇱 Amsterdam Events Feed - Available Commands"
	@echo "=============================================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "📋 Quick Start:"
	@echo "  make install     # Install dependencies"
	@echo "  make scrape      # Run scraper and generate feed"
	@echo "  make wordpress-start  # Start WordPress site"

# Installation and Setup
install: ## Install Python dependencies
	@echo "📦 Installing Python dependencies..."
	pip install -r requirements.txt
	@echo "✅ Dependencies installed!"

# Scraper Commands
scrape: ## Run the Amsterdam events scraper and generate RSS feed
	@echo "🇳🇱 Running Amsterdam Events Scraper..."
	python scrape_amsterdam_events.py
	@echo "✅ Scraper completed!"
	@make status

feed: scrape ## Alias for scrape command

test-scraper: ## Test the scraper without committing results
	@echo "🧪 Testing scraper (backup existing files)..."
	@if [ -f events.xml ]; then cp events.xml events.xml.backup; fi
	@if [ -f events.json ]; then cp events.json events.json.backup; fi
	python scrape_amsterdam_events.py
	@echo "📊 Test Results:"
	@make status
	@echo ""
	@echo "💡 To restore backups: make restore-backup"

restore-backup: ## Restore backed up feed files
	@if [ -f events.xml.backup ]; then mv events.xml.backup events.xml; echo "✅ Restored events.xml"; fi
	@if [ -f events.json.backup ]; then mv events.json.backup events.json; echo "✅ Restored events.json"; fi

# WordPress Commands
wordpress-start: ## Start WordPress and database containers
	@echo "🚀 Starting WordPress environment..."
	docker compose up -d
	@echo "⏳ Waiting for WordPress to be ready..."
	@sleep 10
	@echo "✅ WordPress is starting up!"
	@echo "📱 WordPress Site: http://localhost:8080"
	@echo "🗄️  phpMyAdmin: http://localhost:8081"

wordpress-stop: ## Stop WordPress containers
	@echo "🛑 Stopping WordPress environment..."
	docker compose down
	@echo "✅ WordPress stopped!"

wordpress-restart: ## Restart WordPress containers
	@echo "🔄 Restarting WordPress environment..."
	docker compose restart
	@echo "⏳ Waiting for restart..."
	@sleep 10
	@echo "✅ WordPress restarted!"

wordpress-logs: ## View WordPress container logs
	@echo "📋 WordPress Logs (press Ctrl+C to exit):"
	docker compose logs -f wordpress

wordpress-open: ## Open WordPress in default browser (macOS)
	@echo "🌐 Opening WordPress in browser..."
	@if [ "$(shell uname)" = "Darwin" ]; then \
		open http://localhost:8080; \
	else \
		echo "Please open http://localhost:8080 in your browser"; \
	fi

wordpress-setup: ## Run the WordPress setup script
	@echo "🇳🇱 Running WordPress setup..."
	./setup-local-wordpress.sh

wordpress-reset: ## Reset WordPress (removes all data)
	@echo "⚠️  This will DELETE all WordPress data!"
	@read -p "Are you sure? (y/N): " confirm && [ "$$confirm" = "y" ]
	docker compose down -v
	@echo "🗑️  WordPress data deleted!"
	@echo "💡 Run 'make wordpress-start' to create fresh installation"

# Status and Information
status: ## Show current project status
	@echo "📊 Amsterdam Events Feed - Status"
	@echo "================================="
	@if [ -f events.xml ]; then \
		echo "✅ RSS Feed: events.xml ($(shell ls -lh events.xml | awk '{print $$5}'))"; \
		echo "   Generated: $(shell stat -f '%Sm' events.xml 2>/dev/null || stat -c '%y' events.xml 2>/dev/null || echo 'Unknown')"; \
	else \
		echo "❌ RSS Feed: events.xml not found"; \
	fi
	@if [ -f events.json ]; then \
		event_count=$$(python -c "import json; print(len(json.load(open('events.json'))))" 2>/dev/null || echo "0"); \
		echo "✅ Events Data: events.json ($$event_count events)"; \
	else \
		echo "❌ Events Data: events.json not found"; \
	fi
	@echo "🐳 Docker Status:"
	@if docker compose ps 2>/dev/null | grep -q "running"; then \
		echo "   ✅ WordPress: Running"; \
		echo "   📱 Site: http://localhost:8080"; \
		echo "   🗄️  Admin: http://localhost:8081"; \
	else \
		echo "   ❌ WordPress: Stopped"; \
	fi
	@echo ""
	@echo "🔗 RSS Feed URL for WordPress:"
	@echo "   https://raw.githubusercontent.com/lassebenni/amsterdam-events-feed/master/events.xml"

view-feed: ## View the generated RSS feed in browser
	@if [ -f events.xml ]; then \
		echo "🔍 Opening RSS feed..."; \
		if [ "$(shell uname)" = "Darwin" ]; then \
			open events.xml; \
		else \
			echo "RSS feed location: $(PWD)/events.xml"; \
		fi; \
	else \
		echo "❌ RSS feed not found. Run 'make scrape' first."; \
	fi

view-events: ## View events data in JSON format
	@if [ -f events.json ]; then \
		echo "📋 Events Data:"; \
		python -c "import json; events=json.load(open('events.json')); [print(f'{i+1}. {e[\"title\"]} ({e[\"source\"]})') for i,e in enumerate(events[:10])]"; \
		if [ $$(python -c "import json; print(len(json.load(open('events.json'))))" 2>/dev/null || echo "0") -gt 10 ]; then \
			echo "   ... and more"; \
		fi; \
	else \
		echo "❌ Events data not found. Run 'make scrape' first."; \
	fi

# Development and Maintenance
clean: ## Clean cache files and temporary data
	@echo "🧹 Cleaning cache files..."
	rm -rf __pycache__ .mypy_cache *.pyc
	rm -f *.backup
	@echo "✅ Cache cleaned!"

git-status: ## Show git status and recent commits
	@echo "📊 Git Status:"
	git status --short
	@echo ""
	@echo "📝 Recent Commits:"
	git log --oneline -5

push: ## Add, commit and push changes (prompts for commit message)
	@echo "📤 Preparing to commit and push changes..."
	git add .
	@read -p "Commit message: " msg; \
	git commit -m "$$msg"
	git push
	@echo "✅ Changes pushed to repository!"

# Quick Development Workflow
dev: install scrape wordpress-start ## Complete development setup (install deps, scrape, start WordPress)
	@echo ""
	@echo "🎉 Development environment ready!"
	@echo "📱 WordPress: http://localhost:8080"
	@echo "🔗 RSS Feed: https://raw.githubusercontent.com/lassebenni/amsterdam-events-feed/master/events.xml"

# All-in-one commands
full-test: ## Full test: clean, scrape, start WordPress, show status
	@make clean
	@make scrape
	@make wordpress-start
	@make status
	@echo ""
	@echo "🧪 Full test completed!"

update: ## Update feed and restart WordPress (for testing changes)
	@make scrape
	@make wordpress-restart
	@echo "🔄 Feed updated and WordPress restarted!" 