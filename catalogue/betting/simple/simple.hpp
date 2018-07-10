#pragma once
#include <eosiolib/eosio.hpp>

namespace eosio {

   class betsimple : public contract {
      public:
         betsimple(account_name self): contract(self), counts(_self, _self) {}

         void init(account_name);
	 void create(account_name);
         void accept(account_name);
         void declare(account_name);
	 void destroy(account_name);

	 // @abi table counts i64
	 struct counts{
		 counts(account_name o = account_name()): count(0), owner(o) {}
		 account_name owner;
		 uint64_t count;
		 uint64_t primary_key() const {return owner;}
		 uint64_t incr() {return ++count;}
	 };
	 EOSLIB_SERIALIZE(counts, (owner)(count))

	 typedef eosio::multi_index<N(counts), counts> count_t;
	 count_t counts;
   };

} /// namespace eosio
