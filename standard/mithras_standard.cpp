#pragma once

#include <eosio/chain/block.hpp>
#include <eosiolib/contract.hpp>
#include <string>

namespace mithras {

class standard : public eosio::contract {
	static const account_name mithras_account = N(mithras);

public:
	standard(account_name n) : contract(n) {}
	void message_parties(string message) const {}
	mithras_status get_mithras_status() const {return _status;}
	mithras_version get_mithras_version() const {return "v0.0.1";}
	
	typedef string mithras_status;
	typedef string mithras_version;
	typedef string mithras_message;
	typedef eosio::multi_index<block_id_type, mithras_message> messages;

protected:
	mithras_status _status;
	messages _messages;
};

} /// namespace mithras
