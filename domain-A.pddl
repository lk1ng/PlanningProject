(define (domain drones)
    ; we need strips, types, effects that propagate to other locations, cost tracking
    (:requirements :strips :typing :conditional-effects :action-costs)
    (:types
        drone location supply level - object
    )
    (:predicates
        (at ?d - drone ?where - location) ; a drone is at a location
        (has-supply ?what - supply ?where - location) ; a location has a supply
        (connected ?first - location ?second - location) ; two locations are connected
        (accessible ?where - location) ; a location is drone-accessible
        (battery ?d - drone ?l - level) ; a drone currently has this battery level
        (flight-cost ?from ?to - location ?c - level) ; the flight between ?to and ?from 
                                                          ; has cost ?c in battery levels
        (battery-after ?before ?cost ?left - level) ; battery level after subtracting 
                                                        ; ?cost from "before" is ?left
        (next-battery-level ?before ?post - level) ; for incremental recharging: one level
                                                    ; above ?before is ?post
        (maximum-level ?l - level) ; for complete recharging: defines max level
        (carrying ?d - drone ?what - supply) ; a drone is carrying a supply
        (delivered ?what - supply) ; a supply has been delivered
        (is-charge-station ?where - location) ; a location has a charge station
        (unlocked-by-inspection ?x ?y - location) ; inspecting location ?x unlocks location ?y
        (unlocked-by-delivery ?what - supply ?where - location) ; delivering supply ?what
                                                                    ; unlocks location ?where
        (inspected ?where - location) ; a location has been inspected
        (needs ?what - supply ?where - location) ; a location needs a supply to be delivered
        (empty ?drone - drone) ; a drone is not carrying anything
    )
    (:functions
        (total-cost) - number ; keeps track of total cost of all steps taken thus far
        (distance ?from ?to - location) - number ; static: never changed by any action
    )

    ; fly drone ?d from its current location ?from to a connected location, ?to
    ; expending ?c battery to go from ?before to ?left level.
    (:action fly
    :parameters (?d - drone ?from ?to - location ?before ?c ?left - level)
    :precondition (and
        (at ?d ?from) ; drone has to be at ?from 
        (connected ?from ?to) ; ?from has to be connected to ?to
        (accessible ?to) ; ?to must be accessible
        (battery ?d ?before) ; drone ?d must have battery level ?before
        (flight-cost ?from ?to ?c) ; flight cost between ?to and ?from must be ?c levels
        (battery-after ?before ?c ?left) ; ?before - ?c = ?left 
    )
    :effect (and
        (not (at ?d ?from)) ; ?d no longer at ?from
        (at ?d ?to) ; ?d now at ?to
        (not (battery ?d ?before)) ; ?d's battery is no longer ?before
        (battery ?d ?left) ; ?d now has ?left battery level
        (increase (total-cost) (distance ?from ?to)) ; total cost incremented by distance 
    ))

    ; drone ?d inspects location ?where
    (:action inspect
        :parameters (?d - drone ?where - location)
        :precondition (and 
            (at ?d ?where) ; ?d has to be at ?where
        )
        :effect (and
            (inspected ?where) ; ?where now marked as inspected
            ; all locations unlocked by inspecting ?where are now accessible
            (forall (?y - location) (when (unlocked-by-inspection ?where ?y) (accessible ?y)))
            (increase (total-cost) 1) ; total cost incremented by 1
        )
    )
    
    ; drone ?d picks up supply ?what at location ?where
    (:action pick-up-supply
        :parameters (?d - drone ?where - location ?what - supply)
        :precondition (and 
            (at ?d ?where) ; ?d has to be at ?where
            (has-supply ?what ?where) ; ?where has to have ?what
            (empty ?d) ; ?d must not be carrying anything already
        )
        :effect (and 
            (not (has-supply ?what ?where)) ; ?what no longer at ?where
            (carrying ?d ?what) ; ?d now carrying ?what
            (not (empty ?d)) ; ?d no longer empty
            (increase (total-cost) 1) ; ? increment total cost by 1
        )
    )

    ;drone ?d delivers supply ?what to location ?where that needs it
    (:action deliver-supply
        :parameters (?d - drone ?where - location ?what - supply)
        :precondition (and 
            (needs ?what ?where) ; location ?where needs supply ?what
            (carrying ?d ?what) ; drone is carrying the supply
            (at ?d ?where) ; drone at location
        )
        :effect (and
            (not (carrying ?d ?what)) ; ?d no longer carrying ?what
            (not (needs ?what ?where)) ; ?where no longer needs what
            (has-supply ?what ?where) ; location now has supply
            (delivered ?what) ; supply is now marked as delivered
            (empty ?d) ; drone now empty
            ; any locations unlocked by delivery of this supply are now accessible
            (forall (?y - location) (when (unlocked-by-delivery ?what ?y) (accessible ?y)))
            (increase (total-cost) 1) ; ? increment total cost by 1
        )
    )

    ; Model A: recharge drone to maximum level from its current level
    (:action recharge
        :parameters (?d - drone ?where - location ?before - level ?post - level)
        :precondition (and 
            (is-charge-station ?where) ; location ?where is charge station
            (at ?d ?where) ; drone is at location ?where
            (maximum-level ?post) ; ?post battery level is max level
            (battery ?d ?before) ; ?d starts at battery level ?before
        )
        :effect (and 
            (not (battery ?d ?before)) ; drone no longer at former battery level
            (battery ?d ?post) ; drone now have battery level ?post
            (increase (total-cost) 1) ; ? increment total cost by 1
        )
    )
)
