"""
core/query_engine.py

Advanced query engine for filtering and searching property listings.

Features:
- Price range filtering
- Bedroom/bathroom filtering
- Location-based search
- Property type filtering
- Sorting by multiple fields
- Pagination support
- Text search across multiple fields

Usage:
    from core.query_engine import PropertyQuery

    # Load data
    query = PropertyQuery.from_excel("exports/cleaned/MASTER_CLEANED_WORKBOOK.xlsx")

    # Build query
    results = query.filter(
        price_min=5000000,
        price_max=50000000,
        bedrooms_min=3,
        location="Lekki"
    ).sort_by("price").limit(50).execute()

    # Get results
    for property in results:
        print(f"{property['title']} - {property['price']}")
"""

import os
import logging
from typing import List, Dict, Optional, Any, Callable
from pathlib import Path
import pandas as pd

logger = logging.getLogger(__name__)
RP_DEBUG = os.getenv("RP_DEBUG") == "1"


class PropertyQuery:
    """
    Advanced query engine for property listings.

    Supports filtering, sorting, pagination, and text search.
    """

    def __init__(self, df: pd.DataFrame):
        """
        Initialize query with dataframe.

        Args:
            df: Pandas DataFrame with property listings
        """
        self.original_df = df.copy()
        self.df = df.copy()
        self.filters_applied = []

        if RP_DEBUG:
            logger.debug(f"PropertyQuery initialized with {len(df)} listings")

    @classmethod
    def from_excel(cls, file_path: str, sheet_name: Optional[str] = None) -> 'PropertyQuery':
        """
        Load property data from Excel file.

        Args:
            file_path: Path to Excel file
            sheet_name: Sheet name to load (default: first sheet)

        Returns:
            PropertyQuery instance
        """
        if not Path(file_path).exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        df = pd.read_excel(file_path, sheet_name=sheet_name or 0)
        logger.info(f"Loaded {len(df)} listings from {file_path}")

        return cls(df)

    @classmethod
    def from_csv(cls, file_path: str) -> 'PropertyQuery':
        """
        Load property data from CSV file.

        Args:
            file_path: Path to CSV file

        Returns:
            PropertyQuery instance
        """
        if not Path(file_path).exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        df = pd.read_csv(file_path)
        logger.info(f"Loaded {len(df)} listings from {file_path}")

        return cls(df)

    def filter(self, **kwargs) -> 'PropertyQuery':
        """
        Apply filters to query.

        Supported filters:
            - price_min: Minimum price
            - price_max: Maximum price
            - bedrooms_min: Minimum bedrooms
            - bedrooms_max: Maximum bedrooms
            - bedrooms: Exact number of bedrooms
            - bathrooms_min: Minimum bathrooms
            - bathrooms_max: Maximum bathrooms
            - bathrooms: Exact number of bathrooms
            - property_type: Property type (case-insensitive, partial match)
            - location: Location (case-insensitive, partial match)
            - source: Source site name
            - has_coordinates: Filter properties with/without coordinates

        Args:
            **kwargs: Filter parameters

        Returns:
            Self for chaining
        """
        # Price filters
        if 'price_min' in kwargs and 'price' in self.df.columns:
            price_min = float(kwargs['price_min'])
            self.df = self.df[pd.to_numeric(self.df['price'], errors='coerce').fillna(0) >= price_min]
            self.filters_applied.append(f"price >= {price_min:,.0f}")

        if 'price_max' in kwargs and 'price' in self.df.columns:
            price_max = float(kwargs['price_max'])
            self.df = self.df[pd.to_numeric(self.df['price'], errors='coerce').fillna(float('inf')) <= price_max]
            self.filters_applied.append(f"price <= {price_max:,.0f}")

        # Bedroom filters
        if 'bedrooms' in kwargs and 'bedrooms' in self.df.columns:
            bedrooms = int(kwargs['bedrooms'])
            self.df = self.df[pd.to_numeric(self.df['bedrooms'], errors='coerce').fillna(0) == bedrooms]
            self.filters_applied.append(f"bedrooms = {bedrooms}")

        if 'bedrooms_min' in kwargs and 'bedrooms' in self.df.columns:
            bedrooms_min = int(kwargs['bedrooms_min'])
            self.df = self.df[pd.to_numeric(self.df['bedrooms'], errors='coerce').fillna(0) >= bedrooms_min]
            self.filters_applied.append(f"bedrooms >= {bedrooms_min}")

        if 'bedrooms_max' in kwargs and 'bedrooms' in self.df.columns:
            bedrooms_max = int(kwargs['bedrooms_max'])
            self.df = self.df[pd.to_numeric(self.df['bedrooms'], errors='coerce').fillna(float('inf')) <= bedrooms_max]
            self.filters_applied.append(f"bedrooms <= {bedrooms_max}")

        # Bathroom filters
        if 'bathrooms' in kwargs and 'bathrooms' in self.df.columns:
            bathrooms = int(kwargs['bathrooms'])
            self.df = self.df[pd.to_numeric(self.df['bathrooms'], errors='coerce').fillna(0) == bathrooms]
            self.filters_applied.append(f"bathrooms = {bathrooms}")

        if 'bathrooms_min' in kwargs and 'bathrooms' in self.df.columns:
            bathrooms_min = int(kwargs['bathrooms_min'])
            self.df = self.df[pd.to_numeric(self.df['bathrooms'], errors='coerce').fillna(0) >= bathrooms_min]
            self.filters_applied.append(f"bathrooms >= {bathrooms_min}")

        if 'bathrooms_max' in kwargs and 'bathrooms' in self.df.columns:
            bathrooms_max = int(kwargs['bathrooms_max'])
            self.df = self.df[pd.to_numeric(self.df['bathrooms'], errors='coerce').fillna(float('inf')) <= bathrooms_max]
            self.filters_applied.append(f"bathrooms <= {bathrooms_max}")

        # Property type filter
        if 'property_type' in kwargs and 'property_type' in self.df.columns:
            prop_type = str(kwargs['property_type']).lower()
            self.df = self.df[self.df['property_type'].str.lower().str.contains(prop_type, na=False)]
            self.filters_applied.append(f"property_type contains '{prop_type}'")

        # Location filter
        if 'location' in kwargs and 'location' in self.df.columns:
            location = str(kwargs['location']).lower()
            self.df = self.df[self.df['location'].str.lower().str.contains(location, na=False)]
            self.filters_applied.append(f"location contains '{location}'")

        # Source filter
        if 'source' in kwargs and 'source' in self.df.columns:
            source = str(kwargs['source']).lower()
            self.df = self.df[self.df['source'].str.lower() == source]
            self.filters_applied.append(f"source = '{source}'")

        # Coordinates filter
        if 'has_coordinates' in kwargs:
            has_coords = bool(kwargs['has_coordinates'])
            if 'coordinates' in self.df.columns:
                if has_coords:
                    self.df = self.df[self.df['coordinates'].notna()]
                    self.filters_applied.append("has coordinates")
                else:
                    self.df = self.df[self.df['coordinates'].isna()]
                    self.filters_applied.append("no coordinates")

        if RP_DEBUG and self.filters_applied:
            logger.debug(f"Applied filters: {', '.join(self.filters_applied)}")
            logger.debug(f"Results: {len(self.df)} listings")

        return self

    def search(self, query: str, fields: Optional[List[str]] = None) -> 'PropertyQuery':
        """
        Text search across multiple fields.

        Args:
            query: Search query string (case-insensitive)
            fields: List of fields to search (default: title, location, property_type)

        Returns:
            Self for chaining
        """
        if not query:
            return self

        if fields is None:
            fields = ['title', 'location', 'property_type']

        # Filter to existing columns
        fields = [f for f in fields if f in self.df.columns]

        if not fields:
            logger.warning(f"No valid search fields found. Skipping search.")
            return self

        query_lower = query.lower()
        mask = pd.Series([False] * len(self.df), index=self.df.index)

        for field in fields:
            mask |= self.df[field].str.lower().str.contains(query_lower, na=False)

        self.df = self.df[mask]
        self.filters_applied.append(f"search '{query}' in {', '.join(fields)}")

        if RP_DEBUG:
            logger.debug(f"Search '{query}' found {len(self.df)} results")

        return self

    def sort_by(self, field: str, ascending: bool = True) -> 'PropertyQuery':
        """
        Sort results by field.

        Args:
            field: Column name to sort by
            ascending: Sort order (default: True)

        Returns:
            Self for chaining
        """
        if field not in self.df.columns:
            logger.warning(f"Field '{field}' not found. Skipping sort.")
            return self

        self.df = self.df.sort_values(by=field, ascending=ascending)

        sort_dir = "ascending" if ascending else "descending"
        self.filters_applied.append(f"sorted by {field} ({sort_dir})")

        if RP_DEBUG:
            logger.debug(f"Sorted by {field} ({sort_dir})")

        return self

    def limit(self, n: int, offset: int = 0) -> 'PropertyQuery':
        """
        Limit results (pagination).

        Args:
            n: Number of results to return
            offset: Number of results to skip (default: 0)

        Returns:
            Self for chaining
        """
        self.df = self.df.iloc[offset:offset + n]

        self.filters_applied.append(f"limit {n} offset {offset}")

        if RP_DEBUG:
            logger.debug(f"Limited to {n} results (offset {offset})")

        return self

    def execute(self) -> List[Dict]:
        """
        Execute query and return results as list of dicts.

        Returns:
            List of property dictionaries
        """
        results = self.df.to_dict('records')

        logger.info(f"Query returned {len(results)} results. Filters: {', '.join(self.filters_applied) if self.filters_applied else 'none'}")

        return results

    def to_dataframe(self) -> pd.DataFrame:
        """
        Get results as pandas DataFrame.

        Returns:
            Filtered DataFrame
        """
        return self.df.copy()

    def count(self) -> int:
        """
        Get count of results without executing query.

        Returns:
            Number of results
        """
        return len(self.df)

    def reset(self) -> 'PropertyQuery':
        """
        Reset query to original data.

        Returns:
            Self for chaining
        """
        self.df = self.original_df.copy()
        self.filters_applied = []

        if RP_DEBUG:
            logger.debug("Query reset to original data")

        return self

    def get_summary(self) -> Dict[str, Any]:
        """
        Get summary statistics of current results.

        Returns:
            Dict with summary stats
        """
        summary = {
            'total_results': len(self.df),
            'filters_applied': self.filters_applied.copy(),
        }

        # Price stats
        if 'price' in self.df.columns:
            prices = pd.to_numeric(self.df['price'], errors='coerce').dropna()
            if len(prices) > 0:
                summary['price_stats'] = {
                    'min': float(prices.min()),
                    'max': float(prices.max()),
                    'mean': float(prices.mean()),
                    'median': float(prices.median()),
                }

        # Bedroom stats
        if 'bedrooms' in self.df.columns:
            bedrooms = pd.to_numeric(self.df['bedrooms'], errors='coerce').dropna()
            if len(bedrooms) > 0:
                summary['bedrooms_stats'] = {
                    'min': int(bedrooms.min()),
                    'max': int(bedrooms.max()),
                    'mean': float(bedrooms.mean()),
                }

        # Property type distribution
        if 'property_type' in self.df.columns:
            summary['property_types'] = self.df['property_type'].value_counts().to_dict()

        # Source distribution
        if 'source' in self.df.columns:
            summary['sources'] = self.df['source'].value_counts().to_dict()

        return summary
