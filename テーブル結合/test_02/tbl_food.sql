CREATE TABLE tbl_food (
    food_id INTEGER PRIMARY KEY,
    user_id INTEGER,
    food_content TEXT,
    FOREIGN KEY (user_id) REFERENCES tbl_address (user_id)
);