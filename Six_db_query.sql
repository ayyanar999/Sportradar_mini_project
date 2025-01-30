----- 1) COLLECT THE COMPETITION DATA FROM THE API ENDPOINTS:

----- i)Categories Table

CREATE TABLE Categories(
category_id VARCHAR(50) PRIMARY KEY,        -- Unique ID for the category
category_name VARCHAR(100) NOT NULL         -- Name of the category
)

----- ii)Competitions Table

CREATE TABLE Competitions(
category_id VARCHAR(50),                    -- Links to the category table
competition_id VARCHAR(50) PRIMARY KEY,     -- Unique ID for the competition
competition_name VARCHAR(100) NOT NULL,     -- Name of the competition
parent_id VARCHAR(50) NOT NULL,             -- Parent competition ID
type VARCHAR(20) NOT NULL,                  -- Type of competition (e.g., doubles)
gender VARCHAR(10) NOT NULL                 -- Gender of participants (e.g., men)
)

----- 2) COLLECT THE COMPLEXES DATA FROM THE API ENDPOINTS:

----- i) Complexes Table

CREATE TABLE Complexes(
complex_id VARCHAR(50) PRIMARY KEY,         -- Unique ID for the complex
complex_name VARCHAR(100) NOT NULL          -- Name of the sports complex
) 

----- ii) Venues Table

CREATE TABLE Venues(
venue_id VARCHAR(50) PRIMARY KEY,           -- Unique ID for the venue
venue_name VARCHAR(100) NOT NULL,           -- Name of the venue
city_name VARCHAR(100) NOT NULL,            -- Name of the city
country_name VARCHAR(100) NOT NULL,         -- Name of the country
country_code CHAR(3) NOT NULL,              -- ISO country code
timezone VARCHAR(100) NOT NULL,             -- Timezone of the venue
complex_id VARCHAR(50)                      -- Links to the complexes table
)

----- 3) COLLECT THE DOUBLES COMPETITOR RANKINGS DATA FROM THE API ENDPOINTS

----- i) Competitor_Rankings Table

CREATE TABLE Rankings (
    rank_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY, -- Unique ID for each ranking record
    rank INT NOT NULL,                                    -- Rank of the competitor
    movement INT NOT NULL,                                -- Rank movement compared to the previous week
    points INT NOT NULL,                                  -- Total ranking points
    competitions_played INT NOT NULL,                     -- Number of competitions played
	competitor_id VARCHAR(50)                             -- Links to competitor details
)

------ ii) Competitors Table

CREATE TABLE Competitors(
competitor_id VARCHAR(50) PRIMARY KEY,      -- Unique ID for each competitor
name VARCHAR(100) NOT NULL,                 -- Name of the competitor
country VARCHAR(100) NOT NULL,              -- Competitor's country
country_code CHAR(3) NOT NULL,              -- ISO country code
abbreviation VARCHAR(10) NOT NULL           -- Shortened name/abbreviation of competitor
)

select * from competitions
select * from categories

select * from complexes
select * from venues

select * from rankings
select * from competitors

-- 1) List all competitions along with their category name

SELECT DISTINCT competition_id,competition_name,category_name
                FROM Competitions A JOIN Categories B
				 ON A."category.id"= B.category_id

-- 2) Count the number of competitions in each category

SELECT DISTINCT	category_name,gender, COUNT(*) AS Competition_count
                FROM Competitions A JOIN Categories B
				 ON A."category.id"= B.category_id
				 GROUP BY B.category_name,A.gender,A.competition_name

-- 3) Find all competitions of type 'doubles'

SELECT DISTINCT competition_name,type
                FROM Competitions A JOIN Categories B
				 ON A."category.id"= B.category_id
				 WHERE A."type" = 'doubles'

-- 4) Get competitions that belong to a specific category (e.g., ITF Men)

SELECT DISTINCT competition_name
                FROM Competitions A JOIN Categories B
				 ON A."category.id"= B.category_id
				 WHERE B.category_name ='ITF Men'

-- 5) Identify parent competitions and their sub-competitions

SELECT DISTINCT competition_name
                FROM Competitions A JOIN Categories B
				 ON A."category.id"= B.category_id
				 WHERE A.parent_id IS NOT NULL

-- 6) Analyze the distribution of competition types by category

SELECT DISTINCT	competition_name,type, COUNT(*) AS Competition_count
                FROM Competitions A JOIN Categories B
				 ON A."category.id"= B.category_id
				 GROUP BY A.competition_name,A."type"

-- 7) List all competitions with no parent (top-level competitions)

SELECT DISTINCT competition_name
                FROM Competitions A JOIN Categories B
				 ON A."category.id"= B.category_id
				 WHERE A.parent_id IS NULL		

-- 1) List all venues along with their associated complex name

SELECT DISTINCT venue_name,complex_name
                FROM Venues C JOIN Complexes D
				 ON C.complex_id = D.complex_id

-- 2) Count the number of venues in each complex

SELECT DISTINCT complex_name,d.complex_id,COUNT(venue_name) AS Venue_count
                FROM Venues C JOIN Complexes D
				 ON C.complex_id = D.complex_id
				 GROUP BY complex_name,venue_name,d.complex_id

-- 3) Get details of venues in a specific country (e.g., Chile)

SELECT DISTINCT venue_name
                FROM venues
				WHERE venues.country_name = 'Chile'

-- 4) Identify all venues and their timezones

SELECT DISTINCT venue_name,timezone
                FROM venues
				
-- 5) Find complexes that have more than one venue

SELECT DISTINCT D.complex_id,D.complex_name,COUNT(venue_name) AS venue_count
                FROM Venues C JOIN Complexes D
				 ON C.complex_id = D.complex_id
				 GROUP BY D.complex_id,D.complex_name,C.venue_name
				 HAVING COUNT(venue_name) > 1
				 
-- 6) List venues grouped by country

SELECT country_name,STRING_AGG(DISTINCT venue_name, ',' ORDER BY venue_name) AS venue
                FROM Venues 
				GROUP BY country_name

-- 7) Find all venues for a specific complex (e.g., Nacional)

SELECT DISTINCT venue_name
                FROM Venues C JOIN Complexes D
				 ON C.complex_id = D.complex_id
                 WHERE D.complex_name = 'Nacional'

-- 1) Get all competitors with their rank and points.

SELECT DISTINCT F.name,E.rank,E.points
                FROM Rankings E JOIN Competitors F
				ON E.competitor_id = F.competitor_id

-- 2) Find competitors ranked in the top 5

SELECT DISTINCT F.name,E.rank,E.points
                FROM Rankings E JOIN Competitors F
				ON E.competitor_id = F.competitor_id
                WHERE E.rank <= 5
				ORDER BY E.rank
				
-- 3) List competitors with no rank movement (stable rank)

SELECT DISTINCT F.name,E.rank
                FROM Rankings E JOIN Competitors F
				ON E.competitor_id = F.competitor_id
                WHERE E.movement = 0
				ORDER BY E.rank

-- 4) Get the total points of competitors from a specific country (e.g., Croatia)

SELECT DISTINCT F.name,SUM(E.points)
                FROM Rankings E JOIN Competitors F
				ON E.competitor_id = F.competitor_id
                WHERE F.country = 'Croatia'
				GROUP BY F.name,E.points
				
-- 5) Count the number of competitors per country

SELECT DISTINCT COUNT(name) AS Competitors_count ,country
                FROM Competitors
				GROUP BY country
				
-- 6) Find competitors with the highest points in the current week

SELECT DISTINCT F.name,E.points
                FROM Rankings E JOIN Competitors F
				ON E.competitor_id = F.competitor_id
                WHERE E.points  = (SELECT MAX(points) FROM rankings)


-- select * from users

-- SELECT DISTINCT F.competitor_id, F.name, E.rank, E.points
--                 FROM Rankings E JOIN Competitors F
--                 ON E.competitor_id = F.competitor_id
--                 ORDER BY E.rank, E.points DESC

-- SELECT DISTINCT COUNT(F.name) as total_competitor, AVG(E.points) AS average_points,F.country
--                 FROM Rankings E JOIN Competitors F
--                 ON E.competitor_id = F.competitor_id
--                 GROUP BY F.country,total_competitor DESC;

