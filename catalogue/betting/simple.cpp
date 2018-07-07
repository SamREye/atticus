#include "simple.hpp"

namespace eosio {

void betsimple::create() {
	eosio::print("CREATE");
}

void betsimple::accept() {
	eosio::print("ACCEPT");
}

void betsimple::declare() {
	eosio::print("DECLARE");
}

} /// namespace eosio

EOSIO_ABI( eosio::betsimple, (create)(accept)(declare) )
