(define (problem drones)
    (:domain drones)
    (:objects
        depot charge-station site1 site2 site3 - location
        comms1 - comms
        b0 b1 b2 b3 b4 - level
        drone1 - drone
    )
    (:init
        (= (total-cost) 0)
        ; define node relationships
        (accessible depot) (accessible site1) (accessible site2) (accessible site3) (accessible charge-station)
        (connected depot site1) (connected site1 depot) (flight-cost depot site1 b1) (flight-cost site1 depot b1)
        (connected site1 site2) (connected site2 site1) (flight-cost site2 site1 b1) (flight-cost site1 site2 b1)
        (connected site2 site3) (connected site3 site2) (flight-cost site2 site3 b1) (flight-cost site3 site2 b1)
        (connected site3 charge-station) (connected charge-station site3) (flight-cost site3 charge-station b1) (flight-cost charge-station site3 b1)
        (= (distance depot site1) 1) (= (distance site1 depot) 1) (= (distance site1 site2) 1) (= (distance site2 site1) 1)
        (= (distance site2 site3) 1) (= (distance site3 site2) 1) (= (distance site3 charge-station) 1) (= (distance charge-station site3) 1)
        (is-charge-station charge-station)
        ; define missions
        (needs comms1 site3)
        ; define supply start locations
        (has-supply comms1 depot)
        ; define maths
        (battery-after b4 b1 b3)
        (battery-after b3 b1 b2)
        (battery-after b2 b1 b1)
        (battery-after b1 b1 b0)
        (next-battery-level b0 b1)
        (next-battery-level b1 b2)
        (next-battery-level b2 b3)
        (next-battery-level b3 b4)
        (maximum-level b4)
        ; initial drone state
        (empty drone1)
        (battery drone1 b4)
        (at drone1 depot)
    )
    (:goal (and
        (inspected site1) (inspected site2) (has-supply comms1 site3) (delivered comms1) (at drone1 depot)
    ))
    (:metric minimize (total-cost))
)
