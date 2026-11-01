(define (domain drones)
    (:requirements :strips :typing :negative-preconditions :conditional-effects :action-costs)
    (:types
        drone location supply level - object
        medkit water comms - supply ; these are subtypes of supply
    )
    (:functions
        (total-cost) - number
        (distance ?from ?to - location) - number ; static: never changed by any action
    )
    (:predicates
        (at ?d - drone ?where - location)
        (has-supply ?what - supply ?where - location)
        (connected ?first - location ?second - location)
        (accessible ?where - location)
        (battery ?d - drone ?l - level)
        (flight-cost ?from ?to - location ?c - level)
        (battery-after ?before ?cost ?left - level)
        (next-battery-level ?before ?post - level)
        (maximum-level ?l - level)
        (carrying ?d - drone ?what - supply)
        (delivered ?what - supply)
        (is-charge-station ?where - location)
        (unlocked-by-inspection ?x ?y - location)
        (unlocked-by-delivery ?what - supply ?where - location)
        (inspected ?where - location)
        (needs ?what - supply ?where - location)
        (empty ?drone - drone)
    )
    (:action fly
    :parameters (?d - drone ?from ?to - location ?before ?c ?left - level)
    :precondition (and
        (at ?d ?from)
        (connected ?from ?to)
        (accessible ?to) ; locked locations cannot be entered
        (battery ?d ?before)
        (flight-cost ?from ?to ?c)
        (battery-after ?before ?c ?left) ; only exists if ?before >= ?c
    )
    :effect (and
        (not (at ?d ?from))
        (at ?d ?to)
        (not (battery ?d ?before))
        (battery ?d ?left)
        (increase (total-cost) (distance ?from ?to))
    ))

    (:action inspect
        :parameters (?d - drone ?where - location)
        :precondition (and 
            (at ?d ?where)
        )
        :effect (and
            (inspected ?where)
            (forall (?y - location) (when (unlocked-by-inspection ?where ?y) (accessible ?y)))
        )
    )

    (:action pick-up-supply
        :parameters (?d - drone ?where - location ?what - supply)
        :precondition (and 
            (at ?d ?where)
            (has-supply ?what ?where)
            (empty ?d)
        )
        :effect (and 
            (not (has-supply ?what ?where))
            (carrying ?d ?what)
            (not (empty ?d))
        )
    )

    (:action deliver-supply
        :parameters (?d - drone ?where - location ?what - supply)
        :precondition (and 
            (needs ?what ?where)
            (carrying ?d ?what)
            (at ?d ?where)
        )
        :effect (and
            (not (carrying ?d ?what))
            (not (needs ?what ?where))
            (has-supply ?what ?where)
            (delivered ?what)
            (empty ?d)
            (forall (?y - location) (when (unlocked-by-delivery ?what ?y) (accessible ?y)))
        )
    )

    (:action recharge
        :parameters (?d - drone ?where - location ?before - level ?post - level)
        :precondition (and 
            (is-charge-station ?where)
            (at ?d ?where)
            (maximum-level ?post)
            (battery ?d ?before)
        )
        :effect (and 
            (not (battery ?d ?before))
            (battery ?d ?post)
        )
    )
)
