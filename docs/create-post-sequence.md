# Create Post — Sequence Diagram

```mermaid
sequenceDiagram
    actor User
    participant PostCreate as PostCreate.js
    participant PostManager as PostManager.js
    participant api as api.js
    participant Django as Django urls.py + post_views.py
    participant DRF as DRF TokenAuthentication
    participant ORM as Django ORM
    participant DB as PostgreSQL

    User->>PostCreate: Clicks Save button
    PostCreate->>PostCreate: handleSave() reads title, category_id, content from refs

    PostCreate->>PostManager: createPost with title, category_id, content
    PostManager->>api: authHeader()
    api-->>PostManager: Authorization header with token
    PostManager->>Django: POST /posts with Authorization header and JSON body

    Django->>DRF: Validate token
    DRF->>DB: SELECT from authtoken_token WHERE key matches
    DB-->>DRF: Token row and user_id
    DRF-->>Django: request.user set to RareUser instance

    Django->>ORM: Category.objects.get(pk=category_id)
    ORM->>DB: SELECT from rareapi_category WHERE id matches
    DB-->>ORM: Category row
    ORM-->>Django: Category instance

    Django->>ORM: Post.objects.create with user, category, title, content, publication_date, approved
    ORM->>DB: INSERT INTO rareapi_post
    DB-->>ORM: New Post row
    ORM-->>Django: Post instance

    Django-->>PostManager: 201 Created with post JSON

    alt User selected an image file
        PostManager-->>PostCreate: post object with id
        PostCreate->>PostManager: uploadPostImage with post id and FormData
        PostManager->>api: authHeader()
        api-->>PostManager: Authorization header with token
        PostManager->>Django: PUT /posts/id/image with Authorization header and multipart body
        Django->>Django: Save file to media/post_images/
        Django->>ORM: Update post.image_url and save
        ORM->>DB: UPDATE rareapi_post SET image_url WHERE id matches
        DB-->>ORM: OK
        Django-->>PostManager: 200 OK with image_url
        PostManager-->>PostCreate: response
        PostCreate->>User: navigate to post detail page
    else No image selected
        PostManager-->>PostCreate: post object with id
        PostCreate->>User: navigate to post detail page
    end
```

## Notes

- **Approval**: `approved` is set to `request.user.is_staff` at creation time. Admin posts publish immediately; regular user posts are invisible in all public listings until an admin approves them via `PUT /posts/<id>/approve`.
- **Publication date**: Set server-side to today's date. Posts with a future `publication_date` are filtered out of public listings even if `approved=True`.
- **Image upload**: A separate request after the initial POST — if the image upload fails, the post still exists but without an image.
- **Token lookup**: Every authenticated request triggers a DB query to validate the token. DRF's `TokenAuthentication` handles this before the view function runs.
