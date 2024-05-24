drop table if exists useraccount;
create table useraccount (
id serial primary key,
username VARCHAR (100) not null,
password varchar (254) not null
);

insert into useraccount (username, password) values ('tutorial101', 
'scrypt:32768:8:1$H4snNKslF4eA3qEG$2170eb9a52a9f5a08736bd0d75a9d5c32679df997684f559373ff080afa9bbdec69964829aa0d0e2a0aea7ccb563ebd4e3c103e1e28099679137bcc50e36bacd')

select * from useraccount;