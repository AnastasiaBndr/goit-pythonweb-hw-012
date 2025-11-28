from src.repository import contacts

class TestContactRepository:
    def test_start(self):
        assert True
    # def __init__(self, session: AsyncSession):
    #     self.db = session

    # async def get_contacts(self, skip: int, limit: int, user: User) -> List[Contact]:
    #     query = select(Contact).filter_by(user=user).offset(skip).limit(limit)
    #     tags = await self.db.execute(query)
    #     return tags.scalars().all()

    # async def get_contact_by_id(self, contact_id: int, user: User) -> Contact | None:
    #     query = select(Contact).filter_by(id=contact_id, user=user)
    #     tag = await self.db.execute(query)
    #     return tag.scalar_one_or_none()

    # async def create_contact(self, body: ContactModel, user: User) -> Contact:
    #     data = body.model_dump(exclude_unset=True)

    #     if isinstance(data.get("birthday"), str):
    #         data["birthday"] = datetime.strptime(data["birthday"], "%Y-%m-%d").date()

    #     contact = Contact(**data, user=user)
    #     self.db.add(contact)
    #     await self.db.commit()
    #     await self.db.refresh(contact)
    #     return contact

    # async def update_contact(
    #     self, contact_id: int, body: ContactModel, user: User
    # ) -> Contact | None:
    #     contact = await self.get_contact_by_id(contact_id, user)
    #     if contact:
    #         contact.phone_number = body.phone_number
    #         contact.second_name = body.second_name
    #         contact.first_name = body.first_name
    #         contact.additional_data = body.additional_data
    #         contact.email = body.email
    #         contact.birthday = body.birthday

    #         await self.db.commit()
    #         await self.db.refresh(contact)
    #     return contact

    # async def remove_contact(self, contact_id: int, user: User) -> Contact | None:
    #     contact = await self.get_contact_by_id(contact_id, user)
    #     if contact:
    #         await self.db.delete(contact)
    #         await self.db.commit()
    #     return contact

    # async def search_contacts(
    #     self,
    #     first_name: str = None,
    #     second_name: str = None,
    #     email: str = None,
    #     user: User = None,
    # ) -> Contact | None:
    #     query = select(Contact).filter_by(user=user)

    #     if first_name or second_name or email:
    #         filters = []
    #         if first_name:
    #             filters.append(Contact.first_name.ilike(f"%{first_name}%"))
    #         if second_name:
    #             filters.append(Contact.second_name.ilike(f"%{second_name}%"))
    #         if email:
    #             filters.append(Contact.email.ilike(f"%{email}%"))

    #         query = query.filter(or_(*filters))

    #     result = await self.db.execute(query)
    #     return result.scalars().all()

    # async def get_upcoming_birthdays(self, user: User):
    #     today = date.today()

    #     result = await self.db.execute(select(Contact).filter_by(user=user))
    #     contacts = result.scalars().all()

    #     upcoming = []
    #     for c in contacts:
    #         if not c.birthday:
    #             continue

    #         birthday_this_year = c.birthday.replace(year=today.year)

    #         if birthday_this_year < today:
    #             birthday_this_year = c.birthday.replace(year=today.year + 1)
    #         delta = (birthday_this_year - today).days

    #         if 0 <= delta <= 7:
    #             upcoming.append(c)

    #     return upcoming
