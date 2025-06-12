# Amsterdam Events Feed - Simple Makefile

.PHONY: help scrape wordpress-start wordpress-stop status guide

help: ## Show available commands
	@echo "Amsterdam Events Feed Commands:"
	@echo "  make scrape           - Get new events and generate RSS feed"
	@echo "  make wordpress-start  - Start WordPress site"
	@echo "  make wordpress-stop   - Stop WordPress site"
	@echo "  make status          - Show current status"
	@echo "  make guide           - Render the WordPress admin guide to HTML for browser preview"

scrape: ## Get new events and generate RSS feed
	python scrape_amsterdam_events.py

wordpress-start: ## Start WordPress site
	docker compose up -d

wordpress-stop: ## Stop WordPress site
	docker compose down

status: ## Show RSS feed and WordPress status
	@if [ -f events.xml ]; then echo "✅ RSS feed ready ($(shell wc -l < events.xml) lines)"; else echo "❌ No RSS feed"; fi
	@if docker compose ps 2>/dev/null | grep -q "running"; then echo "✅ WordPress running: http://localhost:8080"; else echo "❌ WordPress stopped"; fi

guide: ## Render the WordPress admin guide to HTML for browser preview
	@pandoc WORDPRESS_ADMIN_GUIDE.md -s -o guide.html 