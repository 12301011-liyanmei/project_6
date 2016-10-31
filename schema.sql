drop table if exists entries;
create table entries (
  id integer primary key autoincrement,
  name text not null,
  password text not null,
  salt text not null
);