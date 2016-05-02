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
  
    return dict(message=T('Welcome to Learn2Cook!'))

@auth.requires_login()
def homepage():
    totalrecs = db(db.question.id>0).count()  # number of records in table (for example)
    showlines = 5    # number of records per page
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
    showlines = 5    # number of records per page
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
def homepage_votes():
    totalrecs = db(db.question.id>0).count()  # number of records in table (for example)
    showlines = 5    # number of records per page
    if len(request.args):
       page=int(request.args[0])
    else:
       page=0
    images=db(db.question.id>0).select(limitby=(page,page+showlines),orderby=~db.question.no_ans)
    
    backward=A('<< previous',_href=URL(r=request,args=[page-showlines])) if page else '<< previous'
    forward=A('next >>',_href=URL(r=request,args=[page+showlines])) if totalrecs>page+showlines else 'next >>'
    nav= "Showing %d to %d out of %d records"  % (page+1, page+len(images), totalrecs)
    return dict(images=images,backward=backward,forward=forward, nav=nav)



@auth.requires_membership('Expert')
def expert_homepage_votes():
    totalrecs = db(db.question.id>0).count()  # number of records in table (for example)
    showlines = 5    # number of records per page
    if len(request.args):
       page=int(request.args[0])
    else:
       page=0
    images=db(db.question.id>0).select(limitby=(page,page+showlines),orderby=~db.question.no_ans)
    
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
    form.vars.asker=image.email
    form.vars.dp=auth.user.dp

    if form.process().accepted:
        response.flash = 'Your answer is posted!'
        usr=db(db.userdata.email==auth.user.email).select().first()
        new_ans=int(image.no_ans)+1
        image.no_ans=new_ans
        image.update_record()
        if usr:
            ans=int(usr.noofans)+1
            usr.noofans=ans
            if ans>=5 and ans<10:
                usr.badge="Bronze"
            elif ans>=10 and ans<15:
                usr.badge="Silver"
            elif ans>=15:
                usr.badge="Gold"
            usr.update_record()
        else:
            db.userdata.insert(email=auth.user.email,noofans=1,badge="Newbie")
            
    usr=db(db.userdata.id>0).select()
    commentss = db(db.answer.question_id==image.id).select()
    views=db(db.expreview.question_id==image.id).select()
    likess=db((db.likes.question_id==image.id) & (db.likes.liker==auth.user.email)).select()
    starss=db((db.stars.question_id==image.id) & (db.stars.user==auth.user.email)).select()
    return dict(image=image, commentss=commentss, likess=likess, starss=starss, views=views, usr=usr, form=form)

@auth.requires_login()
def uploadpage():
    form=SQLFORM(db.question,labels={"title":"Tags"})
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
    tit='%'+str(textbox)+'%'
    if(dropdown=="Title"):
        
        images=db(db.question.title.like(tit, case_sensitive=False)).select(db.question.ALL, orderby=~db.question.timestamp)
    elif(dropdown=="Description"):
        
        images=db(db.question.body.like(tit, case_sensitive=False)).select(db.question.ALL, orderby=~db.question.timestamp)
        
    else:
        images=db(db.question.author.like(tit, case_sensitive=False)).select(db.question.ALL, orderby=~db.question.timestamp)

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
    images=db(db.question.id>0 and db.question.email==auth.user.email).select(limitby=(page,page+showlines),orderby=~db.question.timestamp)
    backward=A('<< previous',_href=URL(r=request,args=[page-showlines])) if page else '<< previous'
    forward=A('next >>',_href=URL(r=request,args=[page+showlines])) if totalrecs>page+showlines else 'next >>'
    nav= "Showing %d to %d out of %d records"  % (page+1, page+len(images), totalrecs)
    return dict(images=images,backward=backward,forward=forward, nav=nav)

@auth.requires_login()
def mystarredquestions():
    
    totalrecs = db(db.stars.user==auth.user.email).count()  # number of records in table (for example)
    showlines = 5    # number of records per page

    if len(request.args):
       page=int(request.args[0])
    else:
       page=0
    listofques=db(db.stars.user==auth.user.email)._select(db.stars.question_id)
    images=db(db.question.id>0 and db.question.id.belongs(listofques)).select(limitby=(page,page+showlines),orderby=~db.question.timestamp)
    backward=A('<< previous',_href=URL(r=request,args=[page-showlines])) if page else '<< previous'
    forward=A('next >>',_href=URL(r=request,args=[page+showlines])) if totalrecs>page+showlines else 'next >>'
    nav= "Showing %d to %d out of %d records"  % (page+1, page+len(images), totalrecs)
    return dict(images=images,backward=backward,forward=forward, nav=nav)

@auth.requires_login()
def feedback():
    form=SQLFORM(db.feed)
    form.vars.author=auth.user.first_name
    form.vars.email=auth.user.email
    form.add_button('Back', URL('homepage'))
    
    if form.process().accepted:
        response.flash="Your feedback is posted!"
        redirect(URL('default','index'))
        
    posts=db(db.feed.id>0).select()
    return dict(form=form,posts=posts)

@auth.requires_login()
def noti():

    rows1=db(db.stars.author==auth.user.email).select(orderby=~db.stars.timestamp)
    rows2=db(db.answer.asker==auth.user.email).select(orderby=~db.answer.timestamp)
    return dict(rows1=rows1,rows2=rows2)

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
        
    return str(image.likes)

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
    return str(image.likes)

@auth.requires_login()
def star():
#     response.flash=BEAUTIFY(request.vars)
    image = db(db.question.id==request.vars.id).select().first()
    starred=db((db.stars.question_id==image.id) & (db.stars.user==auth.user.email)).count()
    if starred==0:
        db.stars.insert(question_id=image.id,user=auth.user.email,username=auth.user.first_name,author=image.email)
        response.flash="Starred"
    else:
        response.flash="Unstarred"
        db((db.stars.question_id==image.id) & (db.stars.user==auth.user.email)).delete()
    return ""

@auth.requires_login()
def edit():
    image = db.question(request.args(0,cast=int)) or redirect(URL('index'))
    form = SQLFORM(db.question,image)
    if form.process().accepted:
        response.flash = 'Your question is edited!'
    return dict(image=image, form=form)
    
    
@auth.requires_login()
def dele():
    db(db.question.id==request.vars.id).delete()
    response.flash="Deleted. Please refresh the page to see the results " 
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
#     response.flash=BEAUTIFY(request.vars.id)
    image = db.question(request.args(0,cast=int)) or redirect(URL('index'))
    form=SQLFORM(db.expreview,labels={"view":"Review"})
    form.vars.question_id=image.id
    if form.process().accepted:
        response.flash="Your review is added"
        redirect(URL('expert_homepage'))
    return dict(form=form)

def autoc():
    text=request.post_vars.text
    typea=request.post_vars.type
    tit=str(text)+'%';
    
    if(typea=="Title"):
        q=0;

    elif(typea=="Description"):

        images=db(db.question.body.like(tit, case_sensitive=False)).select(distinct=True)
#         if(len(images)==0):
#             images=["Abhi"]
        a=["<option value=\""+str(image.body)+"\">" for image in images]
    else:
        images=db(db.question.author.like(tit, case_sensitive=False)).select(distinct=True)
#         if(len(images)==0):
#             images=["Abhi"]
        a=["<option value=\""+str(image.author)+"\">" for image in images]
    if(len(a)==0):
        a=""
    return a
       
    return dict(b=b)
    

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
