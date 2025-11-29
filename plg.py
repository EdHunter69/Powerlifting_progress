def generate_training_plan():
    training_plan = {
        'Day 1': {
            'Focus': 'Heavier Lifts',
            'Lifts': [
                {'lift': 'Squat', 'sets': 3, 'reps': 3, 'intensity': 85},
                {'lift': 'Bench Press', 'sets': 3, 'reps': 3, 'intensity': 85},
                {'lift': 'Deadlift', 'sets': 2, 'reps': 5, 'intensity': 70},
                {'lift': 'Accessory Work', 'sets': 3, 'reps': 8, 'intensity': 65}
            ]
        },
        'Day 2': {
            'Focus': 'Moderate Intensity',
            'Lifts': [
                {'lift': 'Pull-ups', 'sets': 3, 'reps': 6, 'intensity': 70},
                {'lift': 'Incline Press', 'sets': 3, 'reps': 6, 'intensity': 70},
                {'lift': 'Row', 'sets': 3, 'reps': 6, 'intensity': 70}
            ]
        },
        'Day 3': {
            'Focus': 'Explosive Training',
            'Lifts': [
                {'lift': 'Speed Squats', 'sets': 6, 'reps': 2, 'intensity': 70},
                {'lift': 'Moderate Intensity Work', 'sets': 3, 'reps': 5, 'intensity': 75}
            ]
        }
    }

    # Deload Logic
    for day in training_plan:
        for lift in training_plan[day]['Lifts']:
            lift['intensity'] = max(lift['intensity'] - 25, 60)  # Reducing intensity to a minimum of 60%

    return training_plan

# Example usage
if __name__ == '__main__':
    plan = generate_training_plan()
    for day, details in plan.items():
        print(f"{day}: {details}")
