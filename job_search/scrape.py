import requests
from bs4 import BeautifulSoup
import time
import random
from urllib.parse import urlencode
from typing import Dict, List, Optional, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class JobCache:
    """Simple in-memory cache with TTL support"""
    
    def __init__(self, ttl_seconds: int = 3600):  # 1 hour default
        self.cache = {}
        self.ttl = ttl_seconds
    
    def set(self, key: str, value: Any) -> None:
        """Set a value in cache with current timestamp"""
        self.cache[key] = {
            'data': value,
            'timestamp': time.time()
        }
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired"""
        if key not in self.cache:
            return None
        
        item = self.cache[key]
        if time.time() - item['timestamp'] > self.ttl:
            del self.cache[key]
            return None
        
        return item['data']
    
    def clear(self) -> None:
        """Clear expired entries from cache"""
        current_time = time.time()
        expired_keys = [
            key for key, value in self.cache.items()
            if current_time - value['timestamp'] > self.ttl
        ]
        for key in expired_keys:
            del self.cache[key]
    
    def size(self) -> int:
        """Get current cache size"""
        return len(self.cache)

class LinkedInJobScraper:
    """LinkedIn job scraper with caching and error handling"""
    
    def __init__(self):
        self.cache = JobCache()
        self.session = requests.Session()
        
        # Common headers to mimic browser behavior
        self.headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://www.linkedin.com/jobs',
            'X-Requested-With': 'XMLHttpRequest',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
        }
        
        # User agent rotation
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0'
        ]

class Query:
    """Query builder for LinkedIn job searches"""
    
    def __init__(self, query_params: Dict[str, Any]):
        self.host = query_params.get('host', 'www.linkedin.com')
        self.keyword = self._clean_param(query_params.get('keyword', ''))
        self.location = self._clean_param(query_params.get('location', ''))
        self.date_since_posted = query_params.get('dateSincePosted', '')
        self.job_type = query_params.get('jobType', '')
        self.remote_filter = query_params.get('remoteFilter', '')
        self.salary = query_params.get('salary', '')
        self.experience_level = query_params.get('experienceLevel', '')
        self.sort_by = query_params.get('sortBy', '')
        self.limit = int(query_params.get('limit', 0))
        self.page = int(query_params.get('page', 0))
        
        self.scraper = LinkedInJobScraper()
    
    def _clean_param(self, param: str) -> str:
        """Clean and format search parameters"""
        return param.strip().replace(' ', '+') if param else ''
    
    def get_date_since_posted(self) -> str:
        """Convert date range to LinkedIn API format"""
        date_range = {
            'past month': 'r2592000',
            'past week': 'r604800',
            '24hr': 'r86400',
        }
        return date_range.get(self.date_since_posted.lower(), '')
    
    def get_experience_level(self) -> str:
        """Convert experience level to LinkedIn API format"""
        experience_range = {
            'internship': '1',
            'entry level': '2',
            'associate': '3',
            'senior': '4',
            'director': '5',
            'executive': '6',
        }
        return experience_range.get(self.experience_level.lower(), '')
    
    def get_job_type(self) -> str:
        """Convert job type to LinkedIn API format"""
        job_type_range = {
            'full time': 'F',
            'full-time': 'F',
            'part time': 'P',
            'part-time': 'P',
            'contract': 'C',
            'temporary': 'T',
            'volunteer': 'V',
            'internship': 'I',
        }
        return job_type_range.get(self.job_type.lower(), '')
    
    def get_remote_filter(self) -> str:
        """Convert remote filter to LinkedIn API format"""
        remote_filter_range = {
            'on-site': '1',
            'on site': '1',
            'remote': '2',
            'hybrid': '3',
        }
        return remote_filter_range.get(self.remote_filter.lower(), '')
    
    def get_salary(self) -> str:
        """Convert salary to LinkedIn API format"""
        salary_range = {
            40000: '1',
            60000: '2',
            80000: '3',
            100000: '4',
            120000: '5',
        }
        return salary_range.get(self.salary, '')
    
    def get_page_offset(self) -> int:
        """Calculate page offset"""
        return self.page * 25
    
    def build_url(self, start: int = 0) -> str:
        """Build LinkedIn job search URL"""
        base_url = f"https://{self.host}/jobs-guest/jobs/api/seeMoreJobPostings/search?"
        
        params = {}
        
        if self.keyword:
            params['keywords'] = self.keyword
        if self.location:
            params['location'] = self.location
        if self.get_date_since_posted():
            params['f_TPR'] = self.get_date_since_posted()
        if self.get_salary():
            params['f_SB2'] = self.get_salary()
        if self.get_experience_level():
            params['f_E'] = self.get_experience_level()
        if self.get_remote_filter():
            params['f_WT'] = self.get_remote_filter()
        if self.get_job_type():
            params['f_JT'] = self.get_job_type()
        
        params['start'] = str(start + self.get_page_offset())
        
        if self.sort_by == 'recent':
            params['sortBy'] = 'DD'
        elif self.sort_by == 'relevant':
            params['sortBy'] = 'R'
        
        return base_url + urlencode(params)
    
    async def get_jobs(self) -> List[Dict[str, str]]:
        """Fetch all jobs matching the query"""
        return await self._get_jobs_sync()
    
    def _get_jobs_sync(self) -> List[Dict[str, str]]:
        """Synchronous version of get_jobs"""
        all_jobs = []
        start = 0
        batch_size = 25
        has_more = True
        consecutive_errors = 0
        max_consecutive_errors = 3
        
        try:
            # Check cache first
            cache_key = self.build_url(0)
            cached_jobs = self.scraper.cache.get(cache_key)
            if cached_jobs:
                logger.info("Returning cached results")
                return cached_jobs
            
            while has_more:
                try:
                    jobs = self._fetch_job_batch(start)
                    
                    if not jobs:
                        has_more = False
                        break
                    
                    all_jobs.extend(jobs)
                    logger.info(f"Fetched {len(jobs)} jobs. Total: {len(all_jobs)}")
                    
                    if self.limit and len(all_jobs) >= self.limit:
                        all_jobs = all_jobs[:self.limit]
                        break
                    
                    # Reset error counter on successful fetch
                    consecutive_errors = 0
                    start += batch_size
                    
                    # Add delay between requests (2-3 seconds)
                    time.sleep(2 + random.random())
                    
                except Exception as error:
                    consecutive_errors += 1
                    logger.error(f"Error fetching batch (attempt {consecutive_errors}): {str(error)}")
                    
                    if consecutive_errors >= max_consecutive_errors:
                        logger.info("Max consecutive errors reached. Stopping.")
                        break
                    
                    # Exponential backoff
                    time.sleep(2 ** consecutive_errors)
            
            # Cache results if we got any
            if all_jobs:
                self.scraper.cache.set(cache_key, all_jobs)
            
            return all_jobs
            
        except Exception as error:
            logger.error(f"Fatal error in job fetching: {str(error)}")
            raise error
    
    def _fetch_job_batch(self, start: int) -> List[Dict[str, str]]:
        """Fetch a single batch of jobs"""
        headers = self.scraper.headers.copy()
        headers['User-Agent'] = random.choice(self.scraper.user_agents)
        
        try:
            response = self.scraper.session.get(
                self.build_url(start),
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 429:
                raise Exception("Rate limit reached")
            
            response.raise_for_status()
            return self._parse_job_list(response.text)
            
        except requests.exceptions.RequestException as error:
            raise Exception(f"Request failed: {str(error)}")
    
    def _parse_job_list(self, html_content: str) -> List[Dict[str, str]]:
        """Parse job listings from HTML content"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            job_elements = soup.find_all('li')
            
            jobs = []
            for job_element in job_elements:
                try:
                    job_data = self._parse_single_job(job_element)
                    if job_data:
                        jobs.append(job_data)
                except Exception as err:
                    logger.warning(f"Error parsing individual job: {str(err)}")
                    continue
            
            return jobs
            
        except Exception as error:
            logger.error(f"Error parsing job list: {str(error)}")
            return []
    
    def _parse_single_job(self, job_element) -> Optional[Dict[str, str]]:
        """Parse a single job element"""
        try:
            position_elem = job_element.find(class_='base-search-card__title')
            company_elem = job_element.find(class_='base-search-card__subtitle')
            
            if not position_elem or not company_elem:
                return None
            
            position = position_elem.get_text(strip=True)
            company = company_elem.get_text(strip=True)
            
            if not position or not company:
                return None
            
            # Extract other fields
            location_elem = job_element.find(class_='job-search-card__location')
            location = location_elem.get_text(strip=True) if location_elem else ''
            
            date_elem = job_element.find('time')
            date = date_elem.get('datetime') if date_elem else ''
            
            salary_elem = job_element.find(class_='job-search-card__salary-info')
            salary = salary_elem.get_text(strip=True) if salary_elem else 'Not specified'
            
            job_url_elem = job_element.find(class_='base-card__full-link')
            job_url = job_url_elem.get('href') if job_url_elem else ''
            
            company_logo_elem = job_element.find(class_='artdeco-entity-image')
            company_logo = company_logo_elem.get('data-delayed-url') if company_logo_elem else ''
            
            ago_time_elem = job_element.find(class_='job-search-card__listdate')
            ago_time = ago_time_elem.get_text(strip=True) if ago_time_elem else ''
            
            return {
                'position': position,
                'company': company,
                'location': location,
                'date': date,
                'salary': salary,
                'jobUrl': job_url,
                'companyLogo': company_logo,
                'agoTime': ago_time,
            }
            
        except Exception as err:
            logger.warning(f"Error parsing job element: {str(err)}")
            return None

# Main query function (equivalent to module.exports.query)
def query(query_object: Dict[str, Any]) -> List[Dict[str, str]]:
    """Main entry point for job queries"""
    job_query = Query(query_object)
    return job_query._get_jobs_sync()

# Utility functions for cache management
def clear_cache():
    """Clear the job cache"""
    scraper = LinkedInJobScraper()
    scraper.cache.clear()

def get_cache_size() -> int:
    """Get current cache size"""
    scraper = LinkedInJobScraper()
    return scraper.cache.size()

# Example usage
if __name__ == "__main__":
    # Example query
    search_params = {
        'keyword': 'QA',
        'location': ' Australia',
        'dateSincePosted': 'past week',
        'jobType': 'full time',
        'remoteFilter': 'remote',
        'limit': 50
    }
    
    try:
        jobs = query(search_params)
        print(f"Found {len(jobs)} jobs:")
        for i, job in enumerate(jobs[:5], 1):  # Show first 5 jobs
            print(job)
            print(f"{i}. {job['position']} at {job['company']}")
            print(f"   Location: {job['location']}")
            print(f"   Posted: {job['agoTime']}")
            print(f"   Salary: {job['salary']}")
            print(f"   URL: {job['jobUrl']}")
            print("-" * 50)
    except Exception as e:
        print(f"Error: {e}")
