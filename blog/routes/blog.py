from typing import List
from fastapi import APIRouter, Depends, status, Response, HTTPException
from ..schemas import Blog, ShowBlog, User
from ..database import get_db
from .. import models, oauth2
from sqlalchemy.orm import Session

router = APIRouter(
    prefix= '/blog',
    tags= ['blogs']
)


@router.get('/', response_model=List[ShowBlog])
def all_fetch(db: Session = Depends(get_db), current_user: User = Depends(oauth2.get_current_user)):
    blogs = db.query(models.Blog).all()
    return blogs


@router.post("/", status_code=status.HTTP_201_CREATED)
def create(request: Blog, db: Session = Depends(get_db), current_user: User = Depends(oauth2.get_current_user)):
    user_id = [d for d in current_user]
    user_id = user_id[0].id
    new_blog = models.Blog(title=request.title, body=request.body, user_id=user_id)
    db.add(new_blog)
    db.commit()
    db.refresh(new_blog)
    return new_blog


@router.get("/{id}", status_code=status.HTTP_200_OK)
def show(id: int, response: Response, db: Session = Depends(get_db)):
    blog = db.query(models.Blog).filter(models.Blog.id == id).first()
    if not blog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f'Blog with the id {id} is not available.'
        )
    return blog


@router.put('/{id}', status_code=status.HTTP_202_ACCEPTED)
def update(id: int, request: Blog, db: Session = Depends(get_db)):
    blog = db.query(models.Blog).filter(models.Blog.id == id)
    if not blog.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f'Blog with the id {id} is not found'
        )
    blog.update(request.model_dump())
    db.commit()

    return 'Update completed'


@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
def delete(id: int, db: Session = Depends(get_db)):
    db.query(models.Blog).filter(models.Blog.id == id).delete(synchronize_session=False)
    db.commit()

    return 'Deletion completed'