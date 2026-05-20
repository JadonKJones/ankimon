# Event Hooks and Side Effects

*   **`reviewer_did_answer_card`**: Triggers `on_review_card`, main gameloop.
*   **`sync_did_finish`**: Flushes DB to disk to ensure AnkiWeb sync works.
*   **`webview_will_set_content`**: Injects HUD JS/CSS.
