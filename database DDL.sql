create table if not exists clients(
	cedula integer primary key,
	name varchar(30) not null,
	whatsapp varchar(20) not null,
	email varchar(40)
);

create table if not exists orders(
	order_number serial primary key,
	quantity integer not null,
	payment_method varchar(20) not null,
	remarks varchar(150),
	city varchar(30) not null,
	municipality varchar(30) not null,
	cedula integer references clients(cedula),
	total_amount numeric(6,2) not null,
	payment_screenshot varchar(30),
	status varchar(20) not null,
	delivery_amount numeric(5,2),
	datetime timestamp not null
);
