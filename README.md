# fishybot

A [Discord](https://discordapp.com/) fishing mini-game bot inspired by [miso-bot](https://github.com/joinemm/miso-bot/).

```py
+ python3 main.py
        /"*._         _
    .-*'`    `*-.._.-'/
< * ))     ,       (
    `*-._`._(__.--*"`.\
```

The bot provides the following commands:

```
  fishy            Go fishing
  fishystats       Your fish total and type stats
  fishytimer       Time to next fishy
  globalfishystats Fishing leaderboard
  help             Shows this message
  up               Is bot up?
```

## Usage Examples

```
$fishy
you caught 89 uncommon fishy 🐟🐟🐟🐟🐟🐟🐟🐟

$fishystats
you've fished 1182 digital fishy 🎣
+---------------+---------+-------+--------+----------+------+-----------+
|     fisher    | fishies | trash | common | uncommon | rare | legendary |
+---------------+---------+-------+--------+----------+------+-----------+
| John#9999     |   1182  |   3   |   11   |    6     |  0   |     1     |
+---------------+---------+-------+--------+----------+------+-----------+

$fishytimer
sailor you need to wait 3 seconds to fishy 🕒🎣🕒

$globalfishystats
1405 digital fishy fished 🎣
global 🌎 results include gifts 🎁
+---------------+---------+
|     fisher    | fishies |
+---------------+---------+
| John#9999     |   1163  |
| fishybot#1111 |   103   |
| Jack#2222     |   100   |
+---------------+---------+

$up
up! 🐠
```

## Schema

```sql
CREATE TABLE `users` (
  `user_id` bigint NOT NULL,
  `name` varchar(255) NOT NULL,
  `discriminator` int NOT NULL,
  PRIMARY KEY (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci

```
```
mysql> select * from users;
+--------------------+------------+---------------+
| user_id            | name       | discriminator |
+--------------------+------------+---------------+
| 222222222222222222 | John       |          9999 |
| 111111111111111111 | John       |          0000 |
| 333333333333333333 | Jack       |          1111 |
+--------------------+------------+---------------+
```
```sql
CREATE TABLE `fish` (
  `fisher_id` bigint NOT NULL,
  `fish_time` timestamp NOT NULL,
  `fish_amount` int NOT NULL,
  `gift` tinyint NOT NULL DEFAULT '0',
  `gifted_user_id` bigint DEFAULT NULL,
  PRIMARY KEY (`fisher_id`,`fish_time`),
  CONSTRAINT `fish_ibfk_1` FOREIGN KEY (`fisher_id`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
```
```
mysql> select * from fish;
+--------------------+---------------------+-------------+------+--------------------+
| fisher_id          | fish_time           | fish_amount | gift | gifted_user_id     |
+--------------------+---------------------+-------------+------+--------------------+
| 111111111111111111 | 2021-12-11 23:46:53 |           0 |    0 |               NULL |
| 111111111111111111 | 2021-12-11 23:51:28 |         100 |    1 | 222222222222222222 |
| 111111111111111111 | 2021-12-11 23:57:10 |          16 |    0 |               NULL |
| 111111111111111111 | 2021-12-11 23:57:59 |           0 |    1 | 333333333333333333 |
| 111111111111111111 | 2021-12-12 00:21:18 |          87 |    1 | 333333333333333333 |
| 111111111111111111 | 2021-12-12 00:48:09 |         713 |    0 |               NULL |
+--------------------+---------------------+-------------+------+--------------------+
```
