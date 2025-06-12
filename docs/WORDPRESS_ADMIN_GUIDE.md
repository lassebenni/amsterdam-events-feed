# WordPress Admin Guide: Amsterdam Events Feed

This guide walks you through installing the Feedzy RSS Feeds plugin, creating an “Events” page, and viewing your listings at `http://localhost:8080/?page_id=10`.

## Prerequisites

- A running WordPress instance at `http://localhost:8080`
- Admin access to your WordPress site
- An accessible feed file at `/wp-content/themes/custom/events.xml`

---

## 1. Install and Activate Feedzy RSS Feeds Plugin

1. In the WordPress admin sidebar, go to **Plugins > Add New**.
   ![Plugin Search](../screenshots/01-plugin-search.png)
2. In the **Search Plugins** box, type `Feedzy RSS Feeds` and press **Enter**.
   ![Feedzy Search Results](../screenshots/02-feedzy-search.png)
3. Click **Install Now** on the **Feedzy RSS Feeds Lite** card.
   ![Install Feedzy](../screenshots/03-install-feedzy.png)
4. After installation completes, click **Activate**.
   ![Activate Feedzy](../screenshots/04-activate-feedzy.png)

---

## 2. Create the Events Page

1. In the sidebar, go to **Pages > Add New**.
   ![Add New Page](../screenshots/05-add-new-page.png)
2. Enter **Events** as the page title.
3. In the content editor, paste the following shortcode:
   ```
   [feedzy-rss feeds="http://localhost:8080/wp-content/themes/custom/events.xml" max="12"]
   ```
   ![Add Shortcode](../screenshots/06-add-shortcode.png)
4. Click **Publish**.
   ![Publish Events Page](../screenshots/07-publish-page.png)

---

## 3. View Your Events Listing

Open `http://localhost:8080/?page_id=10` in a new browser tab to see the live feed of events:

![Events Listing](../screenshots/08-events-listing.png)

---

*End of Guide* 