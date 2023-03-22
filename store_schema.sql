DROP TABLE IF EXISTS people;
CREATE TABLE people (
  fname     varchar(250) not null,
  loginId   varchar(250) not null,
  email     varchar(250) not null,
  pass      varchar(250) not null,
  primary key (loginId)
);


DROP TABLE IF EXISTS category;
CREATE TABLE category (
  cname     varchar(25) not null,
  cid       int(1),
  primary key (cid),
  unique (cname)
);

DROP TABLE IF EXISTS product;
CREATE TABLE product (
  pid       int(3),
  pname     varchar(250) not null,
  quantity  int(4),
  price     float(5),
  cid       int(1),
  image     varchar(250),
  primary key (pid),
  unique (pname),
  foreign key (cid) references category(cid)
);

DROP TABLE IF EXISTS orders;
CREATE TABLE orders (
  orderDate date,
  orderID   varchar(15),
  loginId   varchar(250) not null,
  total     float(6),
  primary key   (orderID),
  foreign key (loginId) references people(loginId)
);

DROP TABLE IF EXISTS orderItems;
CREATE TABLE orderItems (
  orderItem int(3),
  orderID   varchar(15),
  pid       int(3),
  qty       int(3),
  sumPrice  float(6),
  name      VARCHAR(50),
  primary key   (orderItem),
  foreign key (pid) references product(pid),
  foreign key (orderID) references orders(orderID)
);


INSERT INTO category VALUES ('Phantom','1');
INSERT INTO category VALUES ('Vandal','2');
INSERT INTO category VALUES ('Operator','3');
INSERT INTO category VALUES ('Melee','4');





INSERT INTO product VALUES (001, 'Protocol 781-A', 34, 59.99, 1, 
'/static/protocol.png');
INSERT INTO product VALUES (002, 'SPECTRUM Black', 22, 62.99, 1, '/static/SpectrumBlack.jpg');
INSERT INTO product VALUES (003, 'SPECTRUM White', 16, 75.99, 1, '/static/SpectrumWhite.jpg');
INSERT INTO product VALUES (009, 'Singularity', 8, 200.99, 1,
'/static/singularity.png');

INSERT INTO product VALUES (010, 'ChronoVoid Purple', 43, 49.99, 2, '/static/ChronovoidPurple.jpg');
INSERT INTO product VALUES (012, 'Elderflame Gold', 18, 48.00, 2, '/static/ElderflameVandal.webp');
INSERT INTO product VALUES (014, 'Araxys Purple', 14, 29.00, 2, 
'/static/AraxysVandal.jpg');
INSERT INTO product VALUES (017, 'Champions 2021', 15, 18.00, 2, '/static/Champions.webp');

INSERT INTO product VALUES (024, 'Origin Red', 17, 18.00, 3, 
'/static/OriginRed.jpg');
INSERT INTO product VALUES (025, 'Forsaken Gold', 86, 7.88, 3, 
'/static/ForsakenGold.webp');
INSERT INTO product VALUES (026, 'Reaver Black', 54, 12.99, 3, 
'/static/reaverblack.png');
INSERT INTO product VALUES (028, 'Elderflame Dark', 28, 8.47, 3, 
'/static/elderop.jfif');

INSERT INTO product VALUES (034, 'Gaias Vengeance', 18, 6.50, 4, 
'/static/axe.png');
INSERT INTO product VALUES (035, 'Oni Kumo', 26, 6.50, 4,
'/static/oni.jpg');
INSERT INTO product VALUES (037, 'SPECTRUM Waveform', 17, 21.99, 4, 
'/static/Waveform.webp');
INSERT INTO product VALUES (038, 'Sovereign', 33, 34.00, 4, 
'/static/sovereign.png');



INSERT INTO people Values ('tester', 'testuser', 'tester@gmail.com', 'testpass');