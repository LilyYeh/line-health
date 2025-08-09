# SQLite 常用語法
進入資料庫
> sqlite3 user.db

顯示資料庫裡的所有資料表
> .tables

查看 users 資料表結構
> .schema user

查詢 users 資料表資料
> SELECT * FROM user;

清除 users 資料表資料
> DELETE FROM user WHERE userid = '';

離開 sqlite3
> .exit