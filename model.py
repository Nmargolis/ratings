"""Models and database functions for Ratings project."""

from flask_sqlalchemy import SQLAlchemy

from correlation import pearson

# This is the connection to the SQLite database; we're getting this through
# the Flask-SQLAlchemy helper library. On this, we can find the `session`
# object, where we do most of our interactions (like committing, etc.)

db = SQLAlchemy()


##############################################################################
# Model definitions

class User(db.Model):
    """User of ratings website."""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    email = db.Column(db.String(64), nullable=True)
    password = db.Column(db.String(64), nullable=True)
    age = db.Column(db.Integer, nullable=True)
    zipcode = db.Column(db.String(15), nullable=True)


    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<User user_id=%s email=%s age=%s zipcode=%s>" % (self.user_id, self.email, self.age, self.zipcode)


    def similarity(self, other):

        # create empty list for user 1's ratings
        u_ratings = {}

        # for each rating in user 1's ratings
        for r in self.ratings:
            # add to dictionary u_ratings key value pair of movie_id and associated rating object
            u_ratings[r.movie_id] = r

        #Why do we do the above inside this function, as opposed to adding u_ratings as an attribute of User class?

        # # Peel off first user from other_users
        # o = other_users[0]

        # create empty list of paired ratings
        paired_ratings = []

        # for each rating in the other user's ratings
        for o_rating in other.ratings:
            #look in user 1's dictionary to see if other user's rating's movie_id exists
            u_rating = u_ratings.get(o_rating.movie_id)
            #if user 1 has rated the movie (meaning user u_rating exists)
            if u_rating:
                #create a pair of scores from user 1 and other user
                pair = (u_rating.score, o_rating.score)
                # append pair from ^^ to paired_ratings list
                paired_ratings.append(pair)

        if paired_ratings:
            return pearson(paired_ratings)

        else:
            return 0.0


    def predict_rating(self, movie):
        """Predict user's rating of a movie."""
        
        # Get list of ratings for the movie
        other_ratings = movie.ratings

        
        similarities = []

        # for each rating in other ratings, find the associated user's similarity to self 
        # and store pair of similarity and rating in similarities list
        for r in other_ratings:
            similarity = self.similarity(r.user)
            similarities.append((similarity, r))

        # sort similarities descending
        similarities.sort(reverse=True)

        print similarities
        
        # Pick out top one
        sim, rating = similarities[0]

        # Return predicted score
        return rating.score * sim




class Movie(db.Model):
    """Movies to rate."""

    __tablename__ = "movies"

    movie_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    title = db.Column(db.String(64), nullable=False)
    released_at = db.Column(db.DateTime, nullable=True)
    imdb_url = db.Column(db.String(64), nullable=True)

    def __repr__(self):
        """Provide user-readable information about the movie."""

        return "<Movie movie_id=%s title=%s released_at=%s imdb_url=%s>" % (self.movie_id, 
                                                                             self.title, 
                                                                             self.released_at, 
                                                                             self.imdb_url)

class Rating(db.Model):
    """Ratings by user_id and movie_id"""

    __tablename__ = "ratings"

    rating_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.movie_id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    score = db.Column(db.Integer, nullable=False)

    user = db.relationship("User",
                            backref=db.backref("ratings", order_by=rating_id))
    movie = db.relationship("Movie",
                            backref=db.backref("ratings", order_by=rating_id))



    def __repr__(self):
        """Provide user-readable information about movie ratings."""

        return "<Rating rating_id=%s movie_id=%s user_id=%s score=%s>" % (self.rating_id,
                                                                            self.movie_id, 
                                                                            self.user_id, 
                                                                            self.score)






##############################################################################
# Helper functions

def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our SQLite database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ratings.db'
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app)
    print "Connected to DB."
