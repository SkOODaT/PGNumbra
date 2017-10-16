import random
import time


def spin_pokestop(pgacc, fort, step_location):
    time.sleep(random.uniform(0.8, 1.8))
    response = pgacc.seq_spin_pokestop(fort.id,
                                       fort.latitude,
                                       fort.longitude,
                                       step_location[0],
                                       step_location[1])
    if not response:
        return False

    time.sleep(random.uniform(2, 4))  # Don't let Niantic throttle.

    spin_result = response['FORT_SEARCH'].result
    if spin_result is 1:
        pgacc.log_info('Successfully spun Pokestop for {} XP. Now: Lvl {}, {} / {} XP'.format(
            response['FORT_SEARCH'].experience_awarded,
            pgacc.get_stats('level'), pgacc.get_stats('experience'), pgacc.get_stats('next_level_xp')))
        # Update account stats and clear inventory if necessary.
        result = pgacc.req_level_up_rewards(pgacc.get_stats('level'))['LEVEL_UP_REWARDS'].result
        if result is 1:
            pgacc.log_info('Collected level up rewards for level {}.'.format(pgacc.get_stats('level')))
        else:
            pgacc.log_debug('Already collected level up rewards.')
        return True
    elif spin_result is 2:
        pgacc.log_error('Pokestop was not in range to spin.')
    elif spin_result is 3:
        pgacc.log_error('Failed to spin Pokestop. Has recently been spun.')
    elif spin_result is 4:
        pgacc.log_error('Failed to spin Pokestop. Inventory is full.')
    elif spin_result is 5:
        pgacc.log_error('Maximum number of Pokestops spun for this day.')
    else:
        pgacc.log_error(
            'Failed to spin a Pokestop. Unknown result {}.'.format(spin_result))

    return False
