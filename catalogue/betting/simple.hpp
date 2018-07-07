#pragma once
#include <eosiolib/eosio.hpp>

namespace eosio {

   class betsimple : public contract {
      public:
         betsimple( account_name self ):contract(self){}

         void create();
         void accept();
         void declare();
   };

} /// namespace eosio
