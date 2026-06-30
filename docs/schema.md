# Rare Database Schema

```mermaid
erDiagram
    RareUser {
        int id PK
        string username
        string password
        string first_name
        string last_name
        string email
        bool is_staff
        bool is_active
        bool is_superuser
        datetime date_joined
        datetime last_login
        string bio
        string profile_image_url
        date created_on
    }

    Category {
        int id PK
        string label
    }

    Tag {
        int id PK
        string label
    }

    Reaction {
        int id PK
        string label
        string image_url
    }

    Post {
        int id PK
        int user_id FK
        int category_id FK
        string title
        string content
        date publication_date
        string image_url
        bool approved
    }

    Comment {
        int id PK
        int post_id FK
        int author_id FK
        string subject
        string content
        datetime created_on
    }

    PostTag {
        int id PK
        int post_id FK
        int tag_id FK
    }

    PostReaction {
        int id PK
        int post_id FK
        int reaction_id FK
        int user_id FK
    }

    Subscription {
        int id PK
        int follower_id FK
        int author_id FK
        date created_on
        datetime ended_on
    }

    DemotionQueue {
        int id PK
        string action
        int admin_id FK
        int approver_one_id FK
    }

    RareUser ||--o{ Post : "writes"
    Category ||--o{ Post : "categorizes"
    Post ||--o{ Comment : "has"
    RareUser ||--o{ Comment : "authors"
    Post ||--o{ PostTag : "tagged via"
    Tag ||--o{ PostTag : "applied via"
    Post ||--o{ PostReaction : "receives"
    Reaction ||--o{ PostReaction : "used in"
    RareUser ||--o{ PostReaction : "reacts"
    RareUser ||--o{ Subscription : "follows (follower)"
    RareUser ||--o{ Subscription : "followed by (author)"
    RareUser ||--o{ DemotionQueue : "initiates (admin)"
    RareUser ||--o{ DemotionQueue : "approves (approver_one)"
```

## Notes

- **RareUser** extends Django's `AbstractUser` — `id`, `username`, `password`, `first_name`, `last_name`, `email`, `is_staff`, and `is_active` are inherited fields
- **PostTag** is a join table implementing the Post ↔ Tag many-to-many relationship
- **PostReaction** is a join table implementing the Post ↔ Reaction many-to-many relationship, scoped per user
- **Subscription.ended_on** is nullable — a null value means the subscription is active; a timestamp means it was cancelled (soft delete)
- **DemotionQueue** has a unique constraint on `(action, admin, approver_one)`
