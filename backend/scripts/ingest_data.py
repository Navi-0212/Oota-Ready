"""
Data Ingestion Script
Loads, preprocesses, and ingests restaurant data into the database
"""

import sys
import os
import logging
from pathlib import Path
from tqdm import tqdm
import pandas as pd

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.data_service import DataService, DatasetLoadError
from app.services.data_preprocessor import DataPreprocessor, DataValidationError
from app.db.connection import DatabaseConnection, init_database
from app.db.models import Restaurant

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def ingest_data(
    use_cache: bool = True,
    save_locally: bool = True,
    batch_size: int = 1000
) -> bool:
    """
    Main data ingestion function
    
    Args:
        use_cache: Whether to use cached dataset if available
        save_locally: Whether to save dataset locally
        batch_size: Number of records to insert per batch
        
    Returns:
        True if ingestion successful, False otherwise
    """
    try:
        logger.info("=" * 60)
        logger.info("Starting Data Ingestion Process")
        logger.info("=" * 60)
        
        # Step 1: Load dataset
        logger.info("\n[Step 1/5] Loading dataset...")
        data_service = DataService()
        df = data_service.load_zomato_dataset(use_cache=use_cache)
        
        if save_locally:
            data_service.save_dataset_locally(df)
        
        logger.info(f"✓ Loaded {len(df)} restaurants")
        
        # Step 2: Preprocess data
        logger.info("\n[Step 2/5] Preprocessing data...")
        preprocessor = DataPreprocessor()
        df_clean = preprocessor.clean_data(df)
        df_transformed = preprocessor.transform_data(df_clean)
        
        # Validate data
        is_valid, errors = preprocessor.validate_data(df_transformed)
        if not is_valid:
            logger.error(f"Data validation failed: {errors}")
            return False
        
        logger.info(f"✓ Preprocessed {len(df_transformed)} restaurants")
        
        # Step 3: Initialize database
        logger.info("\n[Step 3/5] Initializing database...")
        db = init_database()
        if not db.test_connection():
            logger.error("Database connection test failed")
            return False
        logger.info("✓ Database initialized")
        
        # Step 4: Ingest data into database
        logger.info("\n[Step 4/5] Ingesting data into database...")
        success_count = 0
        error_count = 0
        
        with db.get_session() as session:
            # Clear existing data (optional - comment out if you want to append)
            logger.info("Clearing existing data...")
            session.query(Restaurant).delete()
            session.commit()
            
            # Insert data in batches
            total_records = len(df_transformed)
            logger.info(f"Inserting {total_records} records in batches of {batch_size}...")
            
            for i in tqdm(range(0, total_records, batch_size), desc="Ingesting"):
                batch = df_transformed.iloc[i:i + batch_size]
                
                for _, row in batch.iterrows():
                    try:
                        restaurant = Restaurant(
                            name=row.get('name', ''),
                            location=row.get('location', ''),
                            cuisine=row.get('cuisine', ''),
                            cost_for_two=float(row.get('cost_for_two', 0)),
                            rating=float(row.get('rating', 0)),
                            votes=int(row.get('votes', 0)) if pd.notna(row.get('votes')) else 0,
                            reviews=row.get('reviews', ''),
                            address=row.get('address', ''),
                            phone=row.get('phone', ''),
                            url=row.get('url', ''),
                            budget_category=row.get('budget_category', ''),
                            rating_category=row.get('rating_category', '')
                        )
                        session.add(restaurant)
                        success_count += 1
                    except Exception as e:
                        error_count += 1
                        logger.warning(f"Failed to insert restaurant {row.get('name', 'unknown')}: {e}")
                
                # Commit batch
                try:
                    session.commit()
                except Exception as e:
                    session.rollback()
                    logger.error(f"Failed to commit batch: {e}")
        
        logger.info(f"✓ Ingestion completed: {success_count} successful, {error_count} errors")
        
        # Step 5: Validate ingestion
        logger.info("\n[Step 5/5] Validating ingestion...")
        with db.get_session() as session:
            db_count = session.query(Restaurant).count()
        
        logger.info(f"✓ Database contains {db_count} restaurants")
        
        if db_count != success_count:
            logger.warning(f"Database count ({db_count}) doesn't match success count ({success_count})")
        
        logger.info("\n" + "=" * 60)
        logger.info("Data Ingestion Process Completed Successfully")
        logger.info("=" * 60)
        
        return True
        
    except DatasetLoadError as e:
        logger.error(f"Dataset loading error: {e}")
        return False
    except DataValidationError as e:
        logger.error(f"Data validation error: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during ingestion: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Ingest restaurant data into database')
    parser.add_argument('--no-cache', action='store_true', help='Disable dataset caching')
    parser.add_argument('--no-save-local', action='store_true', help='Don\'t save dataset locally')
    parser.add_argument('--batch-size', type=int, default=1000, help='Batch size for insertion')
    
    args = parser.parse_args()
    
    success = ingest_data(
        use_cache=not args.no_cache,
        save_locally=not args.no_save_local,
        batch_size=args.batch_size
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
