from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .models import Work

class WorkTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.work_data = {
            'title': 'Test Work',
            'description': 'Test Description',
            'image': None,
            'url': 'https://test.com'
        }
        self.work = Work.objects.create(**self.work_data)

    def test_get_works_list(self):
        """Test retrieving list of works"""
        response = self.client.get(reverse('work-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_work(self):
        """Test creating a new work"""
        new_work_data = {
            'title': 'New Work',
            'description': 'New Description',
            'url': 'https://newtest.com'
        }
        response = self.client.post(reverse('work-list'), new_work_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Work.objects.count(), 2)

    def test_get_work_detail(self):
        """Test retrieving a single work"""
        response = self.client.get(reverse('work-detail', kwargs={'pk': self.work.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.work_data['title'])

    def test_update_work(self):
        """Test updating a work"""
        updated_data = {
            'title': 'Updated Work',
            'description': 'Updated Description',
            'url': 'https://updated.com'
        }
        response = self.client.put(
            reverse('work-detail', kwargs={'pk': self.work.pk}),
            updated_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.work.refresh_from_db()
        self.assertEqual(self.work.title, updated_data['title'])

    def test_delete_work(self):
        """Test deleting a work"""
        response = self.client.delete(reverse('work-detail', kwargs={'pk': self.work.pk}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Work.objects.count(), 0)
