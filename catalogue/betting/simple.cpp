#include "simple.hpp"

namespace bet_simple {

struct impl {
    /**
     * @brief Action to create new bet
     */
    void on(const create& c) {
        require_auth(c.host);
        eosio_assert(c.challenger != c.host, "challenger shouldn't be the same as host");
        eosio::print("Bet created by ", c.host, "--waiting for challenger");
    }

    /**
     * @brief Action to create new bet
     */
    void on(const accept& a) {
        require_auth(a.challenger);
        //eosio_assert()
        eosio::print("Bet is accepted by ", a.challenger);
    }

    /**
     * @brief Action to create new bet
     */
    void on(const declare& d) {
        require_auth(d.expert);
        eosio::print(d.winner, " has been declared the winner");
    }

    void apply( uint64_t /*receiver*/, uint64_t code, uint64_t action ) {
        if (code == code_account) {
            if (action == N(create)) {
                impl::on(eosio::unpack_action_data<bet_simple::create>());
            } else if (action == N(pledge)) {
                impl::on(eosio::unpack_action_data<bet_simple::accept>());
            } else if (action == N(declare)) {
                impl::on(eosio::unpack_action_data<bet_simple::declare>());
            }
        }
    }
};

}

extern "C" {

   using namespace bet_simple;
   /// The apply method implements the dispatch of events to this contract
   void apply( uint64_t receiver, uint64_t code, uint64_t action ) {
      impl().apply(receiver, code, action);
   }    

} // extern "C"
