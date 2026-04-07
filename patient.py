from pydantic import BaseModel,EmailStr,AnyUrl,Field,field_validator,computed_field
from typing import List,Dict,Optional

class Patient(BaseModel):
    name: str
    age: int
    email:EmailStr
    # linkedin_url : AnyUrl
    weight:float
    height:float
    married:bool = False
    allergies:Optional[List[str]] = None
    contact_details:Dict[str,str]

    @field_validator('email')
    @classmethod
    def email_validator(cls,value):

        valid_domains = ['hdfc.com','icici.com']
        domain_name = value.split('@')[-1]

        if domain_name not in valid_domains:
            raise ValueError('Not a valid domain')
        return value
    
    @field_validator('name')
    @classmethod
    def transform_name(cls,value):
        return value.upper()
    
    @computed_field
    @property
    def bmi(self) -> float:
        bmi = round(self.weight/(self.height**2),2)
        return bmi


def insert_patient_data(patient: Patient):
    print(patient.name)
    print(patient.age)
   
    print('inserted')


def update_patient_data(patient: Patient):
    print(patient.name)
    print(patient.age)
    print(patient.bmi)
    print('updated')

patient_info = {'name': 'nitish', 'age': 30,'email':'123@hdfc.com','weight':75.2,'height':1.75,'married':True,'allergies':['pollen','dust'],'contact_details':{'phone_number':'123456'}}
patient1 = Patient(**patient_info)

update_patient_data(patient1)
