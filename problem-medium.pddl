(define (problem drones)
    (:domain drones)
    (:objects
        depot charge-station1 charge-station2 site1 site2 site3 site4 site5 - location
        comms1 - comms
        water1 - water
        medkit1 - medkit
        b0 b1 b2 b3 b4 b5 b6 - level
        drone1 drone2 - drone
    )
    (:init
        (= (total-cost) 0)
        ; define node relationships
        (accessible depot) (accessible site1) (accessible site2) (accessible site3) (accessible site4) (accessible charge-station1) (accessible charge-station2)
        (connected depot site1) (connected site1 depot) (flight-cost depot site1 b1) (flight-cost site1 depot b1)
        (connected depot charge-station1) (connected charge-station1 depot) (flight-cost depot charge-station1 b1) (flight-cost charge-station1 depot b1)
        (connected site1 site2) (connected site2 site1) (flight-cost site2 site1 b2) (flight-cost site1 site2 b2)
        (connected site2 site3) (connected site3 site2) (flight-cost site2 site3 b1) (flight-cost site3 site2 b1)
        (connected site2 charge-station1) (connected charge-station1 site2) (flight-cost site2 charge-station1 b1) (flight-cost charge-station1 site2 b1)
        (connected site2 site5) (connected site5 site2) (flight-cost site2 site5 b1) (flight-cost site5 site2 b1)
        (connected site3 site4) (connected site4 site3) (flight-cost site4 site3 b1) (flight-cost site3 site4 b1)
        (connected site4 charge-station2) (connected charge-station2 site4) (flight-cost site4 charge-station2 b1) (flight-cost charge-station2 site5 b1)
        (= (distance depot site1) 1) (= (distance site1 depot) 1) (= (distance depot charge-station1) 1) (= (distance charge-station1 depot) 1)
        (= (distance site1 site2) 2) (= (distance site2 site1) 2)
        (= (distance site2 site3) 1) (= (distance site3 site2) 1) (= (distance site2 charge-station1) 1) (= (distance charge-station1 site2) 1)
        (= (distance site2 site5) 1) (= (distance site5 site2) 1) (= (distance site3 site4) 1) (= (distance site4 site3) 1)
        (= (distance site4 charge-station2) 1) (= (distance charge-station2 site4) 1)
        (is-charge-station charge-station1)
        (is-charge-station charge-station2)
        ; configure unlocking - site5 unlocked by inspecting site4
        (unlocked-by-inspection site4 site5)
        ; define missions
        (needs comms1 site3)
        (needs water1 site4)
        (needs medkit1 site5)
        ; define supply start locations
        (has-supply comms1 depot)
        (has-supply water1 depot)
        (has-supply medkit1 depot)
        ; define maths
        (battery-after b6 b1 b5)
        (battery-after b5 b1 b4)
        (battery-after b4 b1 b3)
        (battery-after b3 b1 b2)
        (battery-after b2 b1 b1)
        (battery-after b1 b1 b0)
        (battery-after b6 b2 b4)
        (battery-after b5 b2 b3)
        (battery-after b4 b2 b2)
        (battery-after b3 b2 b1)
        (battery-after b2 b2 b0)
        (next-battery-level b0 b1)
        (next-battery-level b1 b2)
        (next-battery-level b2 b3)
        (next-battery-level b3 b4)
        (next-battery-level b4 b5)
        (next-battery-level b5 b6)
        (maximum-level b6)
        ; initial drone state
        (empty drone1)
        (empty drone2)
        (battery drone1 b6)
        (battery drone2 b6)
        (at drone1 depot)
        (at drone2 depot)
    )
    (:goal (and
        (inspected site1) (inspected site3) (inspected site4) (inspected site5) 
        (has-supply comms1 site3) (delivered comms1) (has-supply water1 site4) (delivered water1) 
        (has-supply medkit1 site5) (delivered medkit1) 
        (at drone1 depot) (at drone2 depot)
    ))
    (:metric minimize (total-cost))
)
