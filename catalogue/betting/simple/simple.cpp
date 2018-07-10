#include "simple.hpp"

namespace eosio {

void betsimple::init(account_name user) {
	eosio::print("INIT");
	require_auth(user);
	eosio_assert(counts.find(user) == counts.end(), "Already initialized");
	counts.emplace(user, [&](auto& g) {g.count = 0; g.owner = user;});
	eosio::print("EMPLACED");
	eosio::print("INITED");
}

void betsimple::create(account_name user) {
	eosio::print("CREATING");
	require_auth(user);
	auto it = counts.find(user);
	eosio_assert(it != counts.end(), "Needs initialization");
	counts.modify(it, N(betsimple), [](auto& g) {g.incr();});
	eosio::print("Count: ", it->count);
	eosio::print("CREATED");
}

void betsimple::accept(account_name user) {
	eosio::print("ACCEPTING");
	require_auth(user);
	auto it = counts.find(user);
	eosio_assert(it != counts.end(), "Needs initialization");
	counts.modify(it, N(betsimple), [](auto& g) {g.incr();});
	eosio::print("Count: ", it->count);
	eosio::print("ACCEPTED");
}

void betsimple::declare(account_name user) {
	eosio::print("DELCARING");
	require_auth(user);
	auto it = counts.find(user);
	eosio_assert(it != counts.end(), "Needs initialization");
	counts.modify(it, N(betsimple), [](auto& g) {g.incr();});
	eosio::print("Count: ", it->count);
	eosio::print("DECLARED");
}

void betsimple::destroy(account_name user) {
	eosio::print("DESTROYING");
	require_auth(user);
	auto it = counts.find(user);
	eosio_assert(it != counts.end(), "Needs initialization");
        counts.erase(it);
	eosio::print("DESTROYED");
}

} /// namespace eosio

EOSIO_ABI(eosio::betsimple, (init)(create)(accept)(declare)(destroy))
