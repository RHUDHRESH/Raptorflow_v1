import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
class TestIntakeAPI:
    async def test_create_business(self, client, sample_business):
        """Test business creation"""
        response = client.post('/api/intake', json=sample_business)
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert 'business_id' in data

@pytest.mark.asyncio
class TestResearchAPI:
    async def test_run_research(self, client, mock_perplexity, mock_gemini):
        """Test research endpoint"""
        # First create business
        response = client.post('/api/intake', json={
            'name': 'Test',
            'industry': 'Tech',
            'location': 'Mumbai',
            'description': 'Test',
            'goals': 'Test'
        })
        business_id = response.json()['business_id']
        
        # Run research
        response = client.post(f'/api/research/{business_id}')
        
        assert response.status_code == 200
        data = response.json()
        assert 'competitor_ladder' in data
        assert 'sostac' in data

@pytest.mark.asyncio
class TestPositioningAPI:
    async def test_generate_positioning(self, client, mock_gemini):
        """Test positioning generation"""
        # Setup: create business and run research first
        # ... (setup code)
        
        response = client.post(f'/api/positioning/{business_id}')
        
        assert response.status_code == 200
        data = response.json()
        assert 'options' in data
        assert len(data['options']) == 3
        
        # Validate option structure
        option = data['options'][0]
        assert 'word' in option
        assert 'rationale' in option
        assert 'differentiation_score' in option
