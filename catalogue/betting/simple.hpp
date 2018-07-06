/**
 *  @file
 *  @copyright defined in eos/LICENSE.txt
 */
#pragma once

#include <eosiolib/eosio.hpp>
#include <eosiolib/asset.hpp>

namespace bet_simple {
        static const account_name master = N(bet.simple);
        static const account_name code_account = N(bet.simple);

        struct bet_t {
                account_name host;
                account_name challenger;
                account_name expert;
                eosio::asset amount;

                EOSLIB_SERIALIZE(bet_t, (host)(challenger)(expert)(amount))
        };
        
	/**
	 * @brief Action to create new game
	*/
	struct create {
                account_name host;
                account_name challenger;
                account_name expert;
                eosio::asset amount;
                
                EOSLIB_SERIALIZE(create, (host)(challenger)(expert)(amount))
        };
        
        /**
         * @brief Action to create new game
        */
        struct accept {
                account_name host;
                account_name challenger;
                eosio::asset amount;
                
                EOSLIB_SERIALIZE(accept, (host)(challenger)(amount))
        };
        
        /**
         * @brief Action to create new game
        */
        struct declare {
                account_name host;
                account_name expert;
                account_name winner;
                
                EOSLIB_SERIALIZE(declare, (host)(expert)(winner))
        };

        typedef eosio::multi_index<master, bet_t> bet;
};
