# ============================================================
# ESHShop Database Schema
# Target: MySQL 8.0+
# Character set: utf8mb4 / utf8mb4_unicode_ci
# ============================================================

CREATE DATABASE IF NOT EXISTS eshshop CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE eshshop;

-- -----------------------------------------------------------
-- users: admin accounts
-- -----------------------------------------------------------
CREATE TABLE users (
    id              INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    username        VARCHAR(50)  UNIQUE NOT NULL,
    password_hash   VARCHAR(255) NOT NULL,
    role            ENUM('admin') NOT NULL DEFAULT 'admin',
    display_name    VARCHAR(100) NOT NULL,
    email           VARCHAR(255),
    is_active       TINYINT(1)   NOT NULL DEFAULT 1,
    created_at      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_username (username)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- -----------------------------------------------------------
-- categories: hierarchical product categories
-- -----------------------------------------------------------
CREATE TABLE categories (
    id              INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    parent_id       INT UNSIGNED,
    name            VARCHAR(100) NOT NULL,
    name_en         VARCHAR(100) NOT NULL,
    slug            VARCHAR(100) UNIQUE NOT NULL,
    description     TEXT,
    icon            VARCHAR(255),
    sort_order      INT UNSIGNED NOT NULL DEFAULT 0,
    is_active       TINYINT(1)   NOT NULL DEFAULT 1,
    created_at      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_id) REFERENCES categories(id) ON DELETE SET NULL,
    INDEX idx_slug (slug),
    INDEX idx_parent (parent_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- -----------------------------------------------------------
-- products: core product listing
-- -----------------------------------------------------------
CREATE TABLE products (
    id              INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    category_id     INT UNSIGNED NOT NULL,
    title           VARCHAR(255) NOT NULL,
    title_en        VARCHAR(255),
    description     TEXT,
    description_en  TEXT,
    original_price  DECIMAL(10,2),
    sale_price      DECIMAL(10,2) NOT NULL,
    currency        VARCHAR(3)   NOT NULL DEFAULT 'EUR',
    condition_grade ENUM('new','like_new','good','fair','poor','for_parts') NOT NULL,
    condition_note  TEXT,
    brand           VARCHAR(100),
    tags            JSON,
    status          ENUM('draft','active','sold','archived') NOT NULL DEFAULT 'draft',
    views_count     INT UNSIGNED NOT NULL DEFAULT 0,
    created_by      INT UNSIGNED NOT NULL,
    published_at    DATETIME,
    created_at      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id),
    FOREIGN KEY (created_by)    REFERENCES users(id),
    INDEX idx_category_status  (category_id, status),
    INDEX idx_status_created   (status, created_at DESC),
    INDEX idx_price            (sale_price),
    INDEX idx_condition        (condition_grade)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- -----------------------------------------------------------
-- product_images: multiple images per product
-- -----------------------------------------------------------
CREATE TABLE product_images (
    id              INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    product_id      INT UNSIGNED NOT NULL,
    image_url       VARCHAR(500) NOT NULL,
    thumbnail_url   VARCHAR(500),
    alt_text        VARCHAR(255),
    sort_order      INT UNSIGNED NOT NULL DEFAULT 0,
    is_primary      TINYINT(1)   NOT NULL DEFAULT 0,
    created_at      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    INDEX idx_product (product_id, sort_order)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- -----------------------------------------------------------
-- gdpr_consent_logs: track cookie consent
-- -----------------------------------------------------------
CREATE TABLE gdpr_consent_logs (
    id              BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    session_id      VARCHAR(128) NOT NULL,
    consent_type    ENUM('cookie','newsletter','data_processing') NOT NULL,
    consent_given   TINYINT(1)   NOT NULL,
    ip_address      VARCHAR(45),
    user_agent      VARCHAR(500),
    created_at      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_session (session_id),
    INDEX idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- -----------------------------------------------------------
-- data_deletion_requests: GDPR Article 17 right to erasure
-- -----------------------------------------------------------
CREATE TABLE data_deletion_requests (
    id              BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    email           VARCHAR(255) NOT NULL,
    request_type    ENUM('data_export','data_deletion','rectification') NOT NULL,
    details         TEXT,
    status          ENUM('pending','in_progress','completed','rejected') NOT NULL DEFAULT 'pending',
    admin_notes     TEXT,
    processed_by    INT UNSIGNED,
    processed_at    DATETIME,
    created_at      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (processed_by) REFERENCES users(id),
    INDEX idx_status (status),
    INDEX idx_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- -----------------------------------------------------------
-- operation_logs: audit trail for admin actions
-- -----------------------------------------------------------
CREATE TABLE operation_logs (
    id              BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id         INT UNSIGNED NOT NULL,
    action          VARCHAR(50)  NOT NULL,
    entity_type     VARCHAR(50)  NOT NULL,
    entity_id       INT UNSIGNED,
    details         JSON,
    ip_address      VARCHAR(45),
    created_at      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    INDEX idx_user_created (user_id, created_at),
    INDEX idx_entity (entity_type, entity_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
