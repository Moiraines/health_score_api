#!/usr/bin/env python3
"""
Initialize the database with test data.
"""
import asyncio
import random
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import settings
from app.db.session import async_session
from app.db.models.user import User, UserRole, Gender, ActivityLevel, FitnessGoal
from app.db.models.activity import Activity, ActivityType
from app.db.models.health_record import HealthRecord, HealthMetricType
from app.db.models.sleep import SleepRecord, SleepStage, SleepStageEntry
from app.db.models.walking import WalkingSession, DailyStepGoal, StepRecord
from app.db.models.water import WaterIntake, WaterIntakeGoal
from app.core.security import get_password_hash

async def create_test_users():
    """Create test users with different roles."""
    test_users = [
        {
            "email": "user1@example.com",
            "password": "testpass123",
            "first_name": "John",
            "last_name": "Doe",
            "role": UserRole.USER,
            "gender": Gender.MALE,
            "date_of_birth": datetime(1990, 5, 15).date(),
            "height_cm": 180,
            "weight_kg": 75.5,
            "activity_level": ActivityLevel.MODERATE,
            "fitness_goal": FitnessGoal.WEIGHT_LOSS,
        },
        {
            "email": "trainer@example.com",
            "password": "trainerpass",
            "first_name": "Sarah",
            "last_name": "Smith",
            "role": UserRole.TRAINER,
            "gender": Gender.FEMALE,
            "date_of_birth": datetime(1985, 10, 22).date(),
            "height_cm": 165,
            "weight_kg": 62.0,
            "activity_level": ActivityLevel.HIGH,
            "fitness_goal": FitnessGoal.MUSCLE_GAIN,
        },
        {
            "email": "nutritionist@example.com",
            "password": "nutripass",
            "first_name": "Mike",
            "last_name": "Johnson",
            "role": UserRole.NUTRITIONIST,
            "gender": Gender.MALE,
            "date_of_birth": datetime(1982, 3, 8).date(),
            "height_cm": 175,
            "weight_kg": 80.0,
            "activity_level": ActivityLevel.MODERATE,
            "fitness_goal": FitnessGoal.MAINTENANCE,
        },
    ]
    
    users = []
    async with async_session() as session:
        for user_data in test_users:
            # Check if user already exists
            existing_user = await session.execute(
                User.select().where(User.email == user_data["email"])
            )
            if existing_user.scalar_one_or_none() is not None:
                print(f"User {user_data['email']} already exists, skipping...")
                continue
                
            # Create user
            hashed_password = get_password_hash(user_data.pop("password"))
            user = User(
                **user_data,
                hashed_password=hashed_password,
                is_active=True,
                email_verified=True,
            )
            session.add(user)
            users.append(user)
            print(f"Created user: {user.email}")
        
        await session.commit()
    
    return users

async def create_test_activities(users):
    """Create test activities for users."""
    activities = []
    activity_types = list(ActivityType)
    
    async with async_session() as session:
        for user in users:
            # Create activities for the last 30 days
            for days_ago in range(30):
                activity_date = datetime.utcnow() - timedelta(days=days_ago)
                
                # Skip some days randomly
                if random.random() < 0.3:  # 30% chance to skip a day
                    continue
                
                activity_type = random.choice(activity_types)
                duration = random.randint(20, 120)  # 20-120 minutes
                start_time = activity_date.replace(
                    hour=random.randint(6, 20),  # Between 6 AM and 8 PM
                    minute=random.randint(0, 59),
                    second=0,
                    microsecond=0
                )
                end_time = start_time + timedelta(minutes=duration)
                
                activity = Activity(
                    user_id=user.id,
                    activity_type=activity_type,
                    start_time=start_time,
                    end_time=end_time,
                    duration_minutes=duration,
                    distance_meters=random.randint(1000, 10000) if activity_type in [ActivityType.RUNNING, ActivityType.CYCLING, ActivityType.WALKING] else None,
                    calories_burned=random.uniform(100, 800),
                    average_heart_rate=random.randint(120, 180),
                    max_heart_rate=random.randint(140, 200),
                    notes=f"Test {activity_type.value} activity"
                )
                activities.append(activity)
        
        session.add_all(activities)
        await session.commit()
        print(f"Created {len(activities)} test activities")
    
    return activities

async def create_test_health_records(users):
    """Create test health records for users."""
    records = []
    metric_types = list(HealthMetricType)
    
    async with async_session() as session:
        for user in users:
            # Create daily health records for the last 30 days
            for days_ago in range(30):
                record_date = datetime.utcnow() - timedelta(days=days_ago)
                
                # Weight record
                weight_record = HealthRecord(
                    user_id=user.id,
                    metric_type=HealthMetricType.BODY_WEIGHT,
                    value=random.uniform(60, 100) if user.gender == Gender.MALE else random.uniform(45, 85),
                    unit="kg",
                    recorded_at=record_date,
                    source="test_data"
                )
                records.append(weight_record)
                
                # Random additional metrics
                for _ in range(random.randint(1, 3)):
                    metric_type = random.choice(metric_types)
                    if metric_type == HealthMetricType.BODY_WEIGHT:
                        continue  # Already added
                        
                    if metric_type == HealthMetricType.HEART_RATE:
                        record = HealthRecord(
                            user_id=user.id,
                            metric_type=metric_type,
                            value=random.randint(60, 100),
                            unit="bpm",
                            recorded_at=record_date + timedelta(hours=random.randint(0, 23), minutes=random.randint(0, 59)),
                            source="test_data"
                        )
                    elif metric_type == HealthMetricType.BLOOD_PRESSURE:
                        record = HealthRecord(
                            user_id=user.id,
                            metric_type=metric_type,
                            value=f"{random.randint(100, 140)}/{random.randint(60, 90)}",
                            unit="mmHg",
                            recorded_at=record_date + timedelta(hours=random.randint(0, 23), minutes=random.randint(0, 59)),
                            source="test_data"
                        )
                    else:
                        record = HealthRecord(
                            user_id=user.id,
                            metric_type=metric_type,
                            value=random.uniform(1, 100),
                            recorded_at=record_date + timedelta(hours=random.randint(0, 23), minutes=random.randint(0, 59)),
                            source="test_data"
                        )
                    records.append(record)
        
        session.add_all(records)
        await session.commit()
        print(f"Created {len(records)} test health records")
    
    return records

async def create_test_sleep_records(users):
    """Create test sleep records for users."""
    sleep_records = []
    sleep_stages = list(SleepStage)
    
    async with async_session() as session:
        for user in users:
            # Create sleep records for the last 30 days
            for days_ago in range(1, 31):
                # Sleep time between 9 PM and 12 AM
                sleep_date = (datetime.utcnow() - timedelta(days=days_ago)).replace(hour=22, minute=0, second=0, microsecond=0)
                wake_time = sleep_date + timedelta(hours=random.uniform(6, 9))  # 6-9 hours of sleep
                
                sleep_record = SleepRecord(
                    user_id=user.id,
                    start_time=sleep_date,
                    end_time=wake_time,
                    timezone="UTC",
                    sleep_score=random.randint(60, 100),
                    sleep_efficiency=random.uniform(80, 98),
                    total_sleep_minutes=int((wake_time - sleep_date).total_seconds() / 60),
                    awake_minutes=random.randint(10, 60),
                    light_sleep_minutes=random.randint(180, 300),
                    deep_sleep_minutes=random.randint(60, 120),
                    rem_sleep_minutes=random.randint(60, 120),
                    sleep_latency_minutes=random.randint(5, 30),
                    sleep_interruptions=random.randint(0, 5),
                    device_name="Test Device"
                )
                sleep_records.append(sleep_record)
                
                # Create sleep stages
                stages = []
                current_time = sleep_date
                total_duration = (wake_time - sleep_date).total_seconds() / 60  # in minutes
                
                # Distribute sleep stages throughout the night
                remaining_duration = total_duration
                while remaining_duration > 0:
                    stage = random.choice(sleep_stages)
                    if stage == SleepStage.AWAKE:
                        duration = random.uniform(1, 10)  # Short awake periods
                    else:
                        duration = random.uniform(5, 30)  # Longer sleep stages
                    
                    duration = min(duration, remaining_duration)
                    end_time = current_time + timedelta(minutes=duration)
                    
                    stage_entry = SleepStageEntry(
                        sleep_record=sleep_record,
                        stage=stage,
                        start_time=current_time,
                        end_time=end_time,
                        duration_seconds=int(duration * 60)
                    )
                    stages.append(stage_entry)
                    
                    current_time = end_time
                    remaining_duration -= duration
                    
                    if remaining_duration <= 0:
                        break
                
                session.add_all(stages)
        
        session.add_all(sleep_records)
        await session.commit()
        print(f"Created {len(sleep_records)} test sleep records")
    
    return sleep_records

async def create_test_walking_data(users):
    """Create test walking data for users."""
    walking_sessions = []
    step_records = []
    
    async with async_session() as session:
        for user in users:
            # Create daily step goal
            goal = DailyStepGoal(
                user_id=user.id,
                daily_step_goal=10000,
                reminder_enabled=True,
                reminder_time="20:00"
            )
            await session.merge(goal)
            
            # Create walking data for the last 30 days
            for days_ago in range(30):
                record_date = (datetime.utcnow() - timedelta(days=days_ago)).date()
                
                # Create a walking session
                start_time = datetime.combine(record_date, datetime.min.time()).replace(hour=8, minute=0)
                end_time = start_time + timedelta(minutes=random.randint(20, 120))
                steps = random.randint(1000, 15000)
                distance = steps * 0.000762  # Approx. 0.762 meters per step
                
                session = WalkingSession(
                    user_id=user.id,
                    start_time=start_time,
                    end_time=end_time,
                    steps=steps,
                    distance_meters=distance * 1000,  # Convert to meters
                    calories_burned=steps * 0.04,  # Approx. calories per step
                    active_minutes=int((end_time - start_time).total_seconds() / 60) * 0.8,  # 80% active time
                    average_pace_seconds_per_km=random.uniform(8, 15) * 60,  # 8-15 min/km
                    average_speed_kmh=random.uniform(4, 7.5),  # 4-7.5 km/h
                    average_heart_rate=random.randint(90, 140),
                    max_heart_rate=random.randint(140, 180),
                    device_name="Test Device"
                )
                walking_sessions.append(session)
                
                # Create step record for the day
                step_record = StepRecord(
                    user_id=user.id,
                    date=record_date,
                    steps=steps,
                    distance_meters=distance * 1000,
                    calories_burned=steps * 0.04,
                    active_minutes=int((end_time - start_time).total_seconds() / 60) * 0.8
                )
                step_records.append(step_record)
        
        session.add_all(walking_sessions + step_records)
        await session.commit()
        print(f"Created {len(walking_sessions)} walking sessions and {len(step_records)} step records")
    
    return walking_sessions, step_records

async def create_test_water_intake(users):
    """Create test water intake data for users."""
    water_intakes = []
    
    async with async_session() as session:
        for user in users:
            # Create water intake goal
            goal = WaterIntakeGoal(
                user_id=user.id,
                daily_goal_ml=3000,  # 3L per day
                reminder_enabled=True,
                reminder_start_time="08:00",
                reminder_end_time="20:00",
                reminder_interval_minutes=60
            )
            await session.merge(goal)
            
            # Create water intake records for the last 7 days
            for days_ago in range(7):
                record_date = (datetime.utcnow() - timedelta(days=days_ago)).date()
                
                # 5-10 water intakes per day
                for _ in range(random.randint(5, 10)):
                    intake_time = datetime.combine(
                        record_date,
                        datetime.min.time()
                    ) + timedelta(
                        hours=random.randint(6, 22),  # Between 6 AM and 10 PM
                        minutes=random.randint(0, 59)
                    )
                    
                    intake = WaterIntake(
                        user_id=user.id,
                        amount_ml=random.uniform(100, 400),  # 100-400ml per intake
                        timestamp=intake_time,
                        source=random.choice(["bottle", "glass", "app", "manual"])
                    )
                    water_intakes.append(intake)
        
        session.add_all(water_intakes)
        await session.commit()
        print(f"Created {len(water_intakes)} water intake records")
    
    return water_intakes

async def main():
    """Initialize test data in the database."""
    print("Starting test data initialization...")
    
    # Create test users
    print("\nCreating test users...")
    users = await create_test_users()
    
    # Create test activities
    print("\nCreating test activities...")
    await create_test_activities(users)
    
    # Create test health records
    print("\nCreating test health records...")
    await create_test_health_records(users)
    
    # Create test sleep records
    print("\nCreating test sleep records...")
    await create_test_sleep_records(users)
    
    # Create test walking data
    print("\nCreating test walking data...")
    await create_test_walking_data(users)
    
    # Create test water intake data
    print("\nCreating test water intake data...")
    await create_test_water_intake(users)
    
    print("\nTest data initialization complete!")

if __name__ == "__main__":
    asyncio.run(main())
