# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
#########################################################################

def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html

    if you need a simple wiki simply replace the two lines below with:
    return auth.wiki()
    """
    response.flash = T("Helloooo!!")
    return dict(message=T('Welcome to Learn2Cook!'))

@auth.requires_login()
def homepage():
    totalrecs = db(db.question.id>0).count()  # number of records in table (for example)
    showlines = 25    # number of records per page
    if len(request.args):
       page=int(request.args[0])
    else:
       page=0
    images=db(db.question.id>0).select(limitby=(page,page+showlines),orderby=~db.question.timestamp)
    
    backward=A('<< previous',_href=URL(r=request,args=[page-showlines])) if page else '<< previous'
    forward=A('next >>',_href=URL(r=request,args=[page+showlines])) if totalrecs>page+showlines else 'next >>'
    nav= "Showing %d to %d out of %d records"  % (page+1, page+len(images), totalrecs)
    return dict(images=images,backward=backward,forward=forward, nav=nav)

@auth.requires_membership('Expert')
def expert_homepage():
    totalrecs = db(db.question.id>0).count()  # number of records in table (for example)
    showlines = 25    # number of records per page
    if len(request.args):
       page=int(request.args[0])
    else:
       page=0
    images=db(db.question.id>0).select(limitby=(page,page+showlines),orderby=~db.question.timestamp)
    
    backward=A('<< previous',_href=URL(r=request,args=[page-showlines])) if page else '<< previous'
    forward=A('next >>',_href=URL(r=request,args=[page+showlines])) if totalrecs>page+showlines else 'next >>'
    nav= "Showing %d to %d out of %d records"  % (page+1, page+len(images), totalrecs)
    return dict(images=images,backward=backward,forward=forward, nav=nav)

@auth.requires_login()   
def show():
    image = db.question(request.args(0,cast=int)) or redirect(URL('index'))
    db.answer.question_id.default = image.id
    form = SQLFORM(db.answer)
    form.vars.question_id=image.id
    form.vars.author=auth.user.first_name
    form.vars.email=auth.user.email
    form.vars.likes=0
    
    usr=db1(db1.auth_user.email==auth.user.email).select().first()
    if form.process().accepted:
        response.flash = 'Your answer is posted!'
        new_ans=int(image.no_ans)+1
        image.no_ans=new_ans
        image.update_record()
        
        
#         ans=int(usr.no_ans)+1
#         usr.no_ans=ans
#         usr.update_record()
#         response.flash(usr.no_ans)
        
        
        
    commentss = db(db.answer.question_id==image.id).select()
    views=db(db.review.question_id==image.id).select()
    likess=db((db.likes.question_id==image.id) & (db.likes.liker==auth.user.email)).select()
    return dict(image=image, commentss=commentss, likess=likess, views=views, form=form)



@auth.requires_login()
def uploadpage():
    form=SQLFORM(db.question)
    form.vars.author=auth.user.first_name
    form.vars.email=auth.user.email
    form.add_button('Back', URL('homepage'))
    
    if form.process().accepted:
        response.flash="Your question is posted!"
        redirect(URL('default','homepage'))
    return dict(form=form)


@auth.requires_login()
def search():


    
    dropdown=request.vars.dropdown
    textbox=request.vars.textbox
    
    if(dropdown=="Title"):
        images=db(db.question.title == textbox).select()
    elif(dropdown=="Description"):
        images=db(db.question.body == textbox).select()
    else:
        images=db(db.question.author == textbox).select()
        
    
#     db.question.title.widget = SQLFORM.widgets.autocomplete(request, db.question.title , limitby=(0,10), min_length=2)
#     db.question.body.writable = db.question.body.readable = False
#     db.question.file.writable= db.question.file.readable= False
#     db.question.anonymous.writable= db.question.anonymous.readable= False
#     form=SQLFORM(db.question)
#     title=request.vars.title
#     
#         tit='%'+str(title)+'%'
#         images=db(db.question.title.like(tit, case_sensitive=False)).select()

#         return dict(form=form, images=images)

#     else:
#         return dict(form = form, images="")
    if images:
        return dict(images=images)
    else:
        return dict(images="")

@auth.requires_login()
def myquestions():
    
    totalrecs = db(db.question.email==auth.user.email).count()  # number of records in table (for example)
    showlines = 5    # number of records per page

    if len(request.args):
       page=int(request.args[0])
    else:
       page=0
    rows=db(db.question.id>0 and db.question.email==auth.user.email).select(limitby=(page,page+showlines),orderby=~db.question.timestamp)
    backward=A('<< previous',_href=URL(r=request,args=[page-showlines])) if page else '<< previous'
    forward=A('next >>',_href=URL(r=request,args=[page+showlines])) if totalrecs>page+showlines else 'next >>'
    nav= "Showing %d to %d out of %d records"  % (page+1, page+len(rows), totalrecs)
    return dict(rows=rows,backward=backward,forward=forward, nav=nav)

@auth.requires_login()
def like():
    image = db(db.answer.id==request.vars.id).select().first()
    ques=db(db.question.id==image.question_id).select().first()
    liked=db((db.likes.ans_id==image.id) & (db.likes.liker==auth.user.email)).select().first()
   
    if  liked and int(liked.upordown)==-1:
        new_likes=int(image.likes)+2
        image.likes=new_likes
        image.update_record()
        rec=db((db.likes.ans_id==image.id) & (db.likes.liker==auth.user.email)).select().first()
        rec.upordown=1
        rec.update_record()
    
    elif liked and int(liked.upordown)==1:
        new_likes=int(image.likes)-1;
        image.likes=new_likes;
        image.update_record()
        db((db.likes.ans_id==image.id) & (db.likes.liker==auth.user.email)).delete()
        
    else:
        new_likes=int(image.likes)+1
        image.likes=new_likes
        image.update_record()
        db.likes.insert(question_id=ques.id,ans_id=image.id,liker=auth.user.email,upordown=1)
        
    return str(image.likes)+" Likes"

@auth.requires_login()
def dislike():
    image = db(db.answer.id==request.vars.id).select().first()
    ques=db(db.question.id==image.question_id).select().first()
    liked=db((db.likes.ans_id==image.id) & (db.likes.liker==auth.user.email)).select().first()
   
    if  liked and int(liked.upordown)==1:
        new_likes=int(image.likes)-2
        image.likes=new_likes
        image.update_record()
        rec=db((db.likes.ans_id==image.id) & (db.likes.liker==auth.user.email)).select().first()
        rec.upordown=-1
        rec.update_record()
        
    elif liked and int(liked.upordown)==-1:
        new_likes=int(image.likes)+1;
        image.likes=new_likes;
        image.update_record()
        db((db.likes.ans_id==image.id) & (db.likes.liker==auth.user.email)).delete()
        
    else:
        new_likes=int(image.likes)-1
        image.likes=new_likes
        image.update_record()
        db.likes.insert(question_id=ques.id,ans_id=image.id,liker=auth.user.email,upordown=-1)
    return str(image.likes)+" Likes"

@auth.requires_login()
def edit():
    image = db.question(request.args(0,cast=int)) or redirect(URL('index'))
    form = SQLFORM(db.question,image)
    if form.process().accepted:
        response.flash = 'Your question is edited!'
    return dict(image=image, form=form)
    
    
@auth.requires_login()
def dele():
    remove = db(db.question.id==request.vars.id).delete()
    response.flash="Deleted " 
    return (T("Deleted"))
#     redirect(URL('default','myrecipes'),client_side=True,extension=False,type='auto')


@auth.requires_membership("user_7")
def manage():
    grid = SQLFORM.smartgrid(db1.auth_user,linked_tables=['auth_user'])
    return dict(grid=grid)
    
@auth.requires_membership("user_7")
def managequestions():
    grid = SQLFORM.smartgrid(db.question,linked_tables=['question'])
    return dict(grid=grid)
    

def reviews():
    response.flash="Hello"
#     response.flash=BEAUTIFY(request.vars.id)
    image = db.question(request.args(0,cast=int)) or redirect(URL('index'))
    form=SQLFORM(db.review)
    form.vars.question_id=image.id
    if form.process().accepted:
        response.flash="Your review is added"
    return dict(form=form)

def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/bulk_register
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    also notice there is http://..../[app]/appadmin/manage/auth to allow administrator to manage users
    """
    return dict(form=auth())


@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()
