import pickle
import streamlit as st
import requests
from tenacity import retry, stop_after_attempt, wait_exponential

# Function to fetch movie poster
@retry(stop=stop_after_attempt(3), wait=wait_exponential())
def fetch_poster(movie_id):
    try:
        api_key = "b9f76902b9576cf27215a86e7182a67d"
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=en-US"
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()
        poster_path = data.get('poster_path', '')
        if poster_path:
            return f"https://image.tmdb.org/t/p/w500/{poster_path}"
        else:
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"An error occurred while fetching the poster: {e}")
        return None
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        return None

# Function to recommend movies
def recommend(movie, movies, similarity):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_movie_names = []
    recommended_movie_posters = []
    for i in distances[1:6]:
        # fetch the movie poster
        movie_id = movies.iloc[i[0]].movie_id
        poster = fetch_poster(movie_id)
        if poster:
            recommended_movie_posters.append(poster)
            recommended_movie_names.append(movies.iloc[i[0]].title)

    return recommended_movie_names, recommended_movie_posters

# Main function to create the UI
def main():
    # Set page title and configure layout
    st.set_page_config(page_title="🎬 Ultimate Movie Recommender", page_icon="🌟", layout="wide", initial_sidebar_state="expanded")

    # Load movie data and similarity matrix
    movies = pickle.load(open('movie_list.pkl','rb'))
    similarity = pickle.load(open('similarity.pkl','rb'))

    # Custom CSS for improved styling
    custom_css = """
    body {
        background-color: #f8f9fa;
    }
    .sidebar .sidebar-content {
        background-color: #343a40;
        color: #ffffff;
    }
    .sidebar .sidebar-content .stSelectbox, .sidebar .sidebar-content .stButton {
        color: #ffffff;
    }
    """
    st.markdown(f'<style>{custom_css}</style>', unsafe_allow_html=True)

    # Sidebar with movie selection dropdown
    st.sidebar.title("🎥 Movie Recommender")
    st.sidebar.markdown("Select a movie and click 'Show Recommendations' to discover similar movies.")
    selected_movie = st.sidebar.selectbox("Select a movie", movies['title'].values)
    show_recommendations = st.sidebar.button("Show Recommendations")

    # Main content area
    st.title("🍿 Welcome to the Ultimate Movie Recommender")

    # Display recommendations when button is clicked
    if show_recommendations:
        recommended_movie_names, recommended_movie_posters = recommend(selected_movie, movies, similarity)
        if recommended_movie_names:
            st.subheader("🌟 Top 5 Recommendations")
            col1, col2, col3, col4, col5 = st.columns(5)
            for name, poster, col in zip(recommended_movie_names, recommended_movie_posters, [col1, col2, col3, col4, col5]):
                with col:
                    st.image(poster, use_column_width=True, caption=f"**{name}**")
        else:
            st.warning("No recommendations found for the selected movie.")

if __name__ == "__main__":
    main()
