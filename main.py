import psycopg2

conn = psycopg2.connect(
    dbname="FN27",
    user="postgres",
    password="1",
    host="localhost",
    port="5432"
)
cursor = conn.cursor()


# 1 ----------------------------------------------------------------------------------------------


cursor.execute("""
    CREATE TABLE IF NOT EXISTS categories (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        description TEXT
    );
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS news (
        id SERIAL PRIMARY KEY,
        category_id INTEGER REFERENCES categories(id),
        title VARCHAR(200) NOT NULL UNIQUE,
        content TEXT NOT NULL,
        published_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        is_published BOOLEAN DEFAULT FALSE
    );
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS comments (
        id SERIAL PRIMARY KEY,
        news_id INTEGER REFERENCES news(id),
        author_name VARCHAR(100),
        comment_text TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
""")

conn.commit()

# 2 --------------------------------------------------------------------------------------------------------
cursor.execute("""
    ALTER TABLE news
    ADD COLUMN IF NOT EXISTS views INTEGER DEFAULT 0;
""")

cursor.execute("""
    ALTER TABLE comments
    ALTER COLUMN author_name TYPE TEXT;
""")

conn.commit()


# 3 ---------------------------------------------------------------------------------------------------------

categories = [
    ('Technology', 'Tech-related news'),
    ('Sports', 'All about sports'),
    ('Health', 'Health and wellness tips')
]

cursor.executemany("""
    INSERT INTO categories (name, description)
    VALUES (%s, %s);
""", categories)

news = [
    (1, 'New AI Technology', 'AI is revolutionizing the world.', True),
    (2, 'Sports Event Highlights', 'A great day in sports history.', False),
    (3, 'Health Tips 2024', 'Top tips for a healthy lifestyle.', True)
]

cursor.executemany("""
    INSERT INTO news (category_id, title, content, is_published)
    VALUES (%s, %s, %s, %s);
""", news)

comments = [
    (1, 'Alice', 'Great article on AI!'),
    (2, 'Bob', 'Loved the sports update!'),
    (3, 'Charlie', 'Thanks for the health tips!')
]

cursor.executemany("""
    INSERT INTO comments (news_id, author_name, comment_text)
    VALUES (%s, %s, %s);
""", comments)

conn.commit()


# 4 -----------------------------------------------------------------------------------------------------------


cursor.execute("""
    UPDATE news
    SET views = views + 1;
""")

cursor.execute("""
    UPDATE news
    SET is_published = TRUE
    WHERE published_at < NOW() - INTERVAL '1 day';
""")

conn.commit()


# 5 -------------------------------------------------------------------------------------------------------


cursor.execute("""
    DELETE FROM comments
    WHERE created_at < NOW() - INTERVAL '1 year';
""")

conn.commit()

# 6 ------------------------------------------------------------------------------------------------------


cursor.execute("""
    SELECT n.id AS news_id, n.title AS news_title, c.name AS category_name
    FROM news n
    JOIN categories c ON n.category_id = c.id;
""")
print(cursor.fetchall())

cursor.execute("""
    SELECT * FROM news
    WHERE category_id = (
        SELECT id FROM categories WHERE name = 'Technology'
    );
""")
print(cursor.fetchall())

cursor.execute("""
    SELECT * FROM news
    WHERE is_published = TRUE
    ORDER BY published_at DESC
    LIMIT 5;
""")
print(cursor.fetchall())

cursor.execute("""
    SELECT * FROM news
    WHERE views BETWEEN 10 AND 100;
""")
print(cursor.fetchall())

cursor.execute("""
    SELECT * FROM comments
    WHERE author_name LIKE 'A%';
""")
print(cursor.fetchall())

cursor.execute("""
    SELECT * FROM comments
    WHERE author_name IS NULL;
""")
print(cursor.fetchall())

cursor.execute("""
    SELECT c.name, COUNT(n.id) AS news_count
    FROM categories c
    LEFT JOIN news n ON c.id = n.category_id
    GROUP BY c.name;
""")
print(cursor.fetchall())

# 7 ---------------------------------------------------------------------------------------------------------

cursor.execute("""
    ALTER TABLE news
    ADD CONSTRAINT unique_title UNIQUE (title);
""")

conn.commit()

cursor.close()
conn.close()
