import os
import json
from sqlalchemy import create_engine, Column, Integer, String, Float, Text, MetaData, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Get database URL from environment variables, default to SQLite if not set
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///budget_buddy.db')

# Create engine
engine = create_engine(DATABASE_URL)
Base = declarative_base()

# Define models
class UserProfile(Base):
    __tablename__ = 'user_profiles'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    profile_data = Column(Text)  # Will store JSON data
    
    def __repr__(self):
        return f"<UserProfile(id={self.id}, name={self.name})>"

# Create tables
Base.metadata.create_all(engine)

# Create session
Session = sessionmaker(bind=engine)

def save_profile(name, income, expenses, debts, ef_months, ef_allocation, extra_payment, strategy):
    """
    Save user profile data to database
    
    Parameters:
    -----------
    name : str
        Profile name
    income : float
        Monthly income
    expenses : dict
        Dictionary of expenses
    debts : list
        List of debt dictionaries
    ef_months : int
        Emergency fund months
    ef_allocation : int
        Emergency fund allocation percentage
    extra_payment : float
        Extra payment toward debt
    strategy : str
        Debt payoff strategy
        
    Returns:
    --------
    int
        Profile ID
    """
    session = Session()
    
    # Create profile data dictionary
    profile_data = {
        'income': income,
        'expenses': expenses,
        'debts': debts,
        'ef_months': ef_months,
        'ef_allocation': ef_allocation,
        'extra_payment': extra_payment,
        'strategy': strategy
    }
    
    # Check if profile with same name exists
    existing_profile = session.query(UserProfile).filter(UserProfile.name == name).first()
    
    if existing_profile:
        # Update existing profile
        existing_profile.profile_data = json.dumps(profile_data)
        profile_id = existing_profile.id
    else:
        # Create new profile
        new_profile = UserProfile(
            name=name,
            profile_data=json.dumps(profile_data)
        )
        session.add(new_profile)
        session.flush()
        profile_id = new_profile.id
    
    session.commit()
    session.close()
    
    return profile_id

def load_profile(profile_id=None, name=None):
    """
    Load user profile data from database
    
    Parameters:
    -----------
    profile_id : int, optional
        Profile ID
    name : str, optional
        Profile name
        
    Returns:
    --------
    dict
        Profile data
    """
    session = Session()
    
    # Query by ID or name
    if profile_id is not None:
        profile = session.query(UserProfile).filter(UserProfile.id == profile_id).first()
    elif name is not None:
        profile = session.query(UserProfile).filter(UserProfile.name == name).first()
    else:
        session.close()
        return None
    
    # Return profile data if found
    if profile:
        profile_data = json.loads(profile.profile_data)
        session.close()
        return profile_data
    
    session.close()
    return None

def get_all_profiles():
    """
    Get all user profiles
    
    Returns:
    --------
    list
        List of profile dictionaries with id and name
    """
    session = Session()
    
    profiles = session.query(UserProfile).all()
    
    result = [{'id': p.id, 'name': p.name} for p in profiles]
    
    session.close()
    
    return result

def delete_profile(profile_id):
    """
    Delete user profile
    
    Parameters:
    -----------
    profile_id : int
        Profile ID
        
    Returns:
    --------
    bool
        True if deleted, False otherwise
    """
    session = Session()
    
    profile = session.query(UserProfile).filter(UserProfile.id == profile_id).first()
    
    if profile:
        session.delete(profile)
        session.commit()
        session.close()
        return True
    
    session.close()
    return False
