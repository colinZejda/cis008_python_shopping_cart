"""
purpose:   to store the URL endpoints for the front end of our website
        -- we store the routes (main pages of our website, like login, sign-up, main page, etc)
        -- import Blueprint means we define this file as a blueprint (it has a bunch of URLs/roots in it)
"""
from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from .models import Note, Recommended, IMDB_top_10
from . import db 
from movieREC_use_model import rec_10, titles_only
from imdb_get_top_ten import get_top_10_imdb
import json

views = Blueprint('views', __name__)       # set up a views blueprint for our flask application


@views.route('/home', methods=['GET', 'POST']) # define 1st view (this is a decorator)
@login_required                            # 2nd decorator, cannot get to home pg without loggin in
def home():
    if request.method == 'POST':
        note = request.form.get('note')

        if len(note) < 1:
            flash('Note is too short!', category='error')
        else:
            new_note = Note(data=note, user_id=current_user.id)
            db.session.add(new_note)
            db.session.commit()
            flash('Note added!', category='success')

    return render_template("home.html", user=current_user)

@views.route('/recommend', methods=['GET', 'POST']) # define 1st view (this is a decorator)
@login_required                            # 2nd decorator, cannot get to home pg without loggin in
def recommend():
    for i in range(15):
        old_rec = Recommended.query.first()
        if old_rec:
            if old_rec.user_id == current_user.id:
                db.session.delete(old_rec)
                db.session.commit()
        else:
            break

    if request.method == 'POST':
        user_movie = request.form.get('movie')

        if len(user_movie) < 1:
            flash('Movie title is too short!', category='error')
        else:
            user_movie = user_movie.lower()               # make everything lowercase, then capitalize each word
            user_movie = user_movie.title()
            try:
                x = 1
                ten_rec, found_movie = rec_10(user_movie)
                recommendations = titles_only(str(ten_rec))
                for title in recommendations[:10]:
                    title = str(x) + ') ' + str(title)
                    new_rec = Recommended(data=title, user_id=current_user.id)
                    db.session.add(new_rec)
                    db.session.commit()
                    x += 1
                flash('Movie found!', category='success')

                found_movie = "Our recommendations for you for: " + str(found_movie)
                found_title = Recommended(found_title=found_movie, user_id=current_user.id)
                db.session.add(found_title)
                db.session.commit()
            except:
                flash('Movie not found:(', category='error')

    return render_template("recommend.html", user=current_user)

@views.route('/imdb_top_10', methods=['GET', 'POST']) # define 1st view (this is a decorator)
@login_required                                       # 2nd decorator, cannot get to home pg without loggin in
def imdb_top_10():
    for i in range(20):
        old_top_ten = IMDB_top_10.query.first()
        if old_top_ten:
            if old_top_ten.user_id == current_user.id:
                db.session.delete(old_top_ten)
                db.session.commit()
        else:
            break

    x = 1
    for movie in get_top_10_imdb():
        movie = str(x) + ') ' + str(movie)
        top_ten_movie = IMDB_top_10(data=str(movie), user_id=current_user.id)
        db.session.add(top_ten_movie)
        db.session.commit()
        x += 1

    return render_template("imdb_top_10.html", user=current_user)

@views.route('/delete-note', methods=['POST'])
def delete_note():
    note = json.loads(request.data)      # turn our data into a python dictionary object
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()

    return jsonify({})       # turn the dictionary into a json object (we don't need the dict, but a return is a must)
