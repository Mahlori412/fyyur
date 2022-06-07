#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from distutils.command.config import config
import json
import sys
import dateutil.parser
import babel
from flask import Flask, render_template,jsonify, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
# from models import db, Venue, Artist, Show

#----------------------------------------------------------------------------#
# App Config.

#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)
# TODO: connect to a local postgresql database




#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

from models import *

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data. -- done
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue
  states = []
  venues = Venue.query.distinct(Venue.city).all()
  for venue in venues:
    states.append({
      'city': venue.city,
      'state' : venue.state,
      'venues': []

    })
    # On Single state
  allVenues = Venue.query.all()
  for venue in allVenues:
    for diff_states in states:
      if diff_states['city'] == venue.city:
        diff_states['venues'].append({
          'id': venue.id,
          'name': venue.name,
        })
        upcomingShows = []
        showsAtVenue = Show.query.filter_by(venue_id=venue.id).all()
        for item in showsAtVenue :
          if item.start_time > datetime.now():
            upcomingShows.append({
              'artist_id': item.artist_id,
            })
        diff_states['venues'][-1]['num_upcoming_shows'] = len(upcomingShows)
  
  return render_template('pages/venues.html', areas=states)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee" --done

  # '%{}%' check the string position of the string
  searchVanue = Venue.query.filter(Venue.name.ilike('%{}%'.format(request.form.get('search_term', '')))).all()
  response = {"data": searchVanue, "count": len(searchVanue) }

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id -- done
  # TODO: replace with real venue data from the venues table, using venue_id -- done
  try:
    data = []
    venueDetails = Venue.query.get(venue_id)
    data.append({
      'id': venue_id,
      'name': venueDetails.name,
      'genres': venueDetails.genres.split(','),
      'address': venueDetails.address,
      'city': venueDetails.city,
      'state': venueDetails.state,
      'phone': venueDetails.phone,
      'website_link': venueDetails.website_link,
      'facebook_link': venueDetails.facebook_link,
      'seeking_talent': venueDetails.seeking_talent,
      'seeking_description': venueDetails.seeking_description,
      'image_link': venueDetails.image_link,
      'upcoming_shows': [],
      'past_shows': []
      
    })
    def pastShows(venue_id):
      shows_query = db.session.query(Show).join(Artist).filter(Show.venue_id == venue_id)
      for shows in shows_query:
       if shows.start_time < datetime.now():
            data[0]['past_shows'].append({
              'artist_id': shows.artist_id,
              'artist_name': Artist.query.get(shows.artist_id).name,
              'artist_image_link': Artist.query.get(shows.artist_id).image_link,
              'start_time': shows.start_time.strftime('%Y-%m-%d %H:%M:%S')
            })

            # getting upcoming shows
       else:
          data[0]['upcoming_shows'].append({
            'artist_id': shows.artist_id,
            'artist_name': Artist.query.get(shows.artist_id).name,
            'artist_image_link': Artist.query.get(shows.artist_id).image_link,
            'start_time': shows.start_time.strftime('%Y-%m-%d %H:%M:%S')
          })
          data[0]['upcoming_shows_count'] = len(data[0]['upcoming_shows'])
          data[0]['past_shows_count'] = len(data[0]['past_shows'])
    pastShows(venue_id)
  except:
    print(sys.exc_info())
  finally:
     data = list(filter(lambda info: info['id'] == venue_id, data))[0]

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  forms = request.form

  # meta={'csrf': False} passing parameter in the constructor
  create_venue = VenueForm(meta={'csrf': False})
  
  if not create_venue.validate_on_submit():
    for error in create_venue.errors.keys():
      flash('Error occurred. Venue ' + error + ' could not be listed try again.')
    return render_template('forms/new_venue.html', form=create_venue)
  try:
    # ** means "take all additional named arguments to this function and insert them into this parameter as dictionary entries
    # Reference Stackoverflow.com
    venue = Venue(**create_venue.data)
    db.session.add(venue)
    db.session.commit()
    flash('Venue ' + venue.name + ' was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Venue ' + forms.get('name') + ' could not be listed.')
  finally:
    db.session.close()
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>/delete', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using --done
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    venue = Venue.query.with_entities(Venue.name).filter_by(id=venue_id).first()
    # query shows table to find all the shows at that venue_id
    show = Show.query.filter_by(venue_id=venue_id).all()
    #if shows have such venue first delete them to prevent break in the app
    # if no shows, delete the venue from the db.venues table and flash the success message
    if len(show) == 0:
      Venue.query.filter_by(id=venue_id).delete()
      db.session.commit()
    if len(show) > 0:
      Show.query.filter_by(venue_id=venue_id).delete()
      Venue.query.filter_by(id=venue_id).delete()
      db.session.commit()
    flash('Venue ' + venue.name + ' was successfully deleted!')
  except: 
    db.session.rollback()
    print(sys.exc_info())
    flash(' Error occurred. Venue ' + venue.name + ' could not be deleted.')
  finally:
    db.session.close()
    return {'success': True}


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database

  artists =[Artist.id,Artist.name]

  data = Artist.query.with_entities(*artists)
 
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  
  ## '%{}%' check the string position of the string
  data = Artist.query.filter(Artist.name.ilike('%{}%'.format(request.form.get('search_term', '')))).all()
  response = {"count": len(data), "data": data }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  artistDetails = Artist.query.get(artist_id)
  data = {}
  data['id'] = artistDetails.id
  data['name'] = artistDetails.name
  data['city'] = artistDetails.city
  data['state'] =artistDetails.state
  data['phone'] = artistDetails.phone
  data['genres'] = artistDetails.genres.split(',')
  data['website_link'] = artistDetails.website_link
  data['facebook_link'] = artistDetails.facebook_link
  data['seeking_venue'] = artistDetails.seeking_venue
  data['seeking_description'] = artistDetails.seeking_description
  data['image_link'] = artistDetails.image_link
  data['upcoming_shows'] = []
  data['past_shows'] = []
  

  showsQuery = Show.query.filter_by(artist_id=artist_id).all()
  for allshows in showsQuery:
    if allshows.start_time > datetime.now():
      data['upcoming_shows'].append({
        "venue_id": allshows.venue_id,
        "venue_name": allshows.venue.name,
        "venue_image_link": allshows.venue.image_link,
        "start_time": str(allshows.start_time)
      })
    else:
      data['past_shows'].append({
        "venue_id": allshows.venue_id,
        "venue_name": allshows.venue.name,
        "venue_image_link": allshows.venue.image_link,
        "start_time": str(allshows.start_time)
      })
  data['past_shows_count'] = len(data['past_shows'])
  data['upcoming_shows_count'] = len(data['upcoming_shows'])

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  # TODO: populate form with fields from artist with ID <artist_id>
  artist = Artist.query.get(artist_id)
  form = ArtistForm(obj=artist)
   # we gonna populate the form with the data of the artist we are editing
  
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  try:
    # get the data with the artist_id we are editing
    artist = Artist.query.get(artist_id)
    artist.name = request.form.get('name')
    artist.city = request.form.get('city')
    artist.state = request.form.get('state')
    artist.phone = request.form.get('phone')
    artist.genres = json.dumps(genres.data)
    artist.website_link = request.form.get('website_link')
    def genres():
      genre = ''
      data = request.form.getlist('genres')
      for t in data:
        genre = genre + t + ','
      return genre
    artist.genres = genres()
    artist.facebook_link = request.form.get('facebook_link')
    artist.seeking_description = request.form.get('seeking_description')
    artist.image_link = request.form.get('image_link')
    def seeking_venue():
      if request.form.get('seeking_venue') == 'y':
        return True
      else:
        return False
    artist.seeking_venue = seeking_venue()
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully updated!')
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be updated.')
  finally:
    db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue = Venue.query.get(venue_id)
  form = VenueForm(obj=venue)
  # TODO: populate form with values from venue with ID <venue_id> 
  venue = Venue.query.get(venue_id)
  print(venue)
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  try:
    editVenue = Venue.query.get(venue_id)
    editVenue.name = request.form['name']
    editVenue.phone = request.form['phone']
    editVenue.state = request.form['state']
    editVenue.city = request.form['city']
    editVenue.address = request.form['address']
    
    def genres():
      genre = ''
      data = request.form.getlist('genres')
      for t in data:
        genre = genre + t + ','
      return genre
    editVenue.genres =  genres()
    
    editVenue.image_link = request.form['image_link']
    editVenue.facebook_link = request.form['facebook_link']
    editVenue.website_link = request.form['website_link']
    def values():
      if request.form['seeking_talent'] == 'y':
        return True
      else:
        return False
    editVenue.seeking_talent = values()
    editVenue.seeking_description = request.form['seeking_description']
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully updated!')
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be updated.')
  finally:
    db.session.close()

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  forms = request.form
  artist_form = ArtistForm(meta={'csrf': False})

  if not artist_form.validate_on_submit():
    
    for error in artist_form.errors.keys():
      flash('Error occurred. Venue ' + error + ' could not be listed try again.')
    
    # This avoids user from re-entering the values into form.
    return render_template('forms/new_artist.html', form=artist_form)

  try:
    artist = Artist(**artist_form.data)
    json.dumps(artist_form.genres.data)
    db.session.add(artist)
    db.session.commit()
    flash('Venue ' + artist.name + ' was successfully listed!')
  except:
    db.session.rollback()  
    flash('An error occurred. Venue ' + forms.get('name') + ' could not be listed.')
  finally:
    db.session.close()
  return render_template('pages/home.html')

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  allshows = db.session.query(Show).join(Artist).join(Venue).all()

  data = []

  for show in allshows:
    
    currentArtist = show.artist_id
    artistInfo = Artist.query.get(currentArtist)
    currentVenue = show.venue_id
    venueInfo = Venue.query.get(currentVenue)
    data.append({
      "artist_id": artistInfo.id,
      "venue_id": venueInfo.id,
      "venue_name": venueInfo.name,
      "artist_name": artistInfo.name,
      "artist_image_link": artistInfo.image_link,
      "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S') 
    })
    
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  try:
    data = request.form
    artist_id = data['artist_id']
    venue_id = data['venue_id']
    start_date = data['start_time']
    shows = Show(artist_id=artist_id, venue_id=venue_id, start_time=start_date)
    db.session.add(shows)
    db.session.commit()
    flash('Show was successfully listed!')
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occurred. Show could not be listed.')
  finally:
    db.session.close()
  
  
  return render_template('pages/home.html')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
