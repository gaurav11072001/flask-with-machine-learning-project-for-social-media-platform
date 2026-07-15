#!/usr/bin/env python3
"""
Cybercrime Dataset Generator for XAI Training
This module creates a comprehensive dataset of cybercrime-related text samples
"""

import pandas as pd
import numpy as np
import json
import random
from datetime import datetime, timedelta
import re

class CybercrimeDatasetGenerator:
    """Generate comprehensive cybercrime dataset for training XAI models"""
    
    def __init__(self):
        self.categories = {
            'financial_fraud': {
                'severity': 'high',
                'description': 'Financial scams, money transfer requests, fake investment schemes'
            },
            'phishing': {
                'severity': 'high', 
                'description': 'Attempts to steal personal information, login credentials'
            },
            'threats_violence': {
                'severity': 'critical',
                'description': 'Physical threats, violence, intimidation'
            },
            'cyberbullying': {
                'severity': 'medium',
                'description': 'Online harassment, bullying, hate speech'
            },
            'illegal_drugs': {
                'severity': 'high',
                'description': 'Drug trafficking, illegal substance sales'
            },
            'weapons_trafficking': {
                'severity': 'critical',
                'description': 'Illegal weapons sales, trafficking'
            },
            'identity_theft': {
                'severity': 'high',
                'description': 'Stealing personal information, identity fraud'
            },
            'romance_scam': {
                'severity': 'medium',
                'description': 'Fake romantic relationships for financial gain'
            },
            'safe': {
                'severity': 'none',
                'description': 'Normal, safe conversations'
            }
        }
        
        self.financial_fraud_samples = [
            "I need you to send $500 to help with my emergency",
            "Can you transfer money to this account for investment opportunity",
            "Send bitcoin to this address for guaranteed returns",
            "Western Union transfer required for lottery winnings",
            "Need your bank details for international money transfer",
            "PayPal payment required to unlock your inheritance",
            "Wire transfer needed for business partnership",
            "Send money through MoneyGram for urgent medical bills",
            "Crypto payment needed for exclusive trading tips",
            "Cash advance required for real estate investment",
            "Quick loan available, just send processing fee first",
            "Government refund available, send personal details",
            "Foreign lottery winner, pay taxes to claim prize",
            "Investment scheme with 500% returns guaranteed",
            "Nigerian prince needs help transferring millions"
        ]
        
        self.phishing_samples = [
            "Click this link to verify your account immediately",
            "Your password will expire, update it now",
            "Suspicious activity detected, confirm your identity",
            "Account locked, provide login details to unlock",
            "Banking security update required, enter credentials",
            "Free gift card, just enter your personal information",
            "Tax refund available, submit SSN and bank details",
            "Credit score update, verify with credit card info",
            "PayPal account suspended, confirm payment details",
            "Amazon package delivery failed, update address and payment",
            "Microsoft security alert, verify Windows license",
            "Google account compromised, reset password here",
            "iPhone winner selected, claim prize with personal info",
            "Social media account hacked, secure it now"
        ]
        
        self.threats_violence_samples = [
            "I'm going to kill you if you don't listen",
            "Watch your back, I know where you live",
            "I have weapons and I'm not afraid to use them",
            "You're going to pay for this with blood",
            "I'll hurt you and your family",
            "Bomb threat at your location",
            "Bring a knife to our meeting",
            "Violence is the only solution here",
            "I'll shoot anyone who gets in my way",
            "Meet me for a fight, bring your friends",
            "Death threats are just the beginning",
            "Armed and dangerous, stay away",
            "Explosive device planted in your area",
            "Assassination planned for tonight"
        ]
        
        self.cyberbullying_samples = [
            "You're so stupid, no one likes you",
            "Kill yourself, the world would be better",
            "Fat loser, go hide in your room",
            "Spread rumors about this person to everyone",
            "Post embarrassing photos of them online",
            "Nobody wants to be your friend",
            "You're ugly and worthless",
            "Everyone is laughing at you behind your back",
            "You don't belong here, go away",
            "Share this person's private information",
            "Make fake accounts to harass them",
            "You're a failure at everything",
            "Your family must be ashamed of you"
        ]
        
        self.illegal_drugs_samples = [
            "Selling cocaine, high quality stuff",
            "Marijuana delivery available 24/7",
            "Heroin supplier, discreet transactions",
            "Meth lab products for sale",
            "Ecstasy pills, party supplies available",
            "Fentanyl dealer, bulk discounts",
            "LSD tabs, premium quality",
            "Prescription drugs without prescription",
            "Crack cocaine, street prices",
            "Synthetic drugs, new formulas",
            "Drug trafficking route established",
            "Smuggling operation needs partners"
        ]
        
        self.weapons_trafficking_samples = [
            "Guns for sale, no background check needed",
            "Illegal firearms dealer, cash only",
            "Explosive materials available for purchase",
            "Ammunition supplier, bulk quantities",
            "Weapon modifications and upgrades",
            "Military grade equipment for civilians",
            "Homemade weapons instructions included",
            "Assault rifles, automatic weapons available",
            "Bomb making materials and tutorials",
            "Weapon smuggling across borders"
        ]
        
        self.identity_theft_samples = [
            "Selling stolen social security numbers",
            "Credit card information for sale",
            "Fake IDs and documents available",
            "Personal data from recent breach",
            "Login credentials for various accounts",
            "Medical records and insurance info",
            "Driver's license numbers for identity theft",
            "Passport information for document fraud",
            "Banking details from phishing campaigns",
            "Complete identity packages for sale"
        ]
        
        self.romance_scam_samples = [
            "I love you but need money for travel",
            "Emergency happened, send money for hospital",
            "My account is frozen, help with finances",
            "Meeting delayed, need funds for new ticket",
            "Family crisis requires immediate cash",
            "Stranded in foreign country, need money home",
            "Military deployment, need financial support",
            "Business opportunity needs investment from you",
            "Grandmother sick, need money for medicine",
            "Visa problems, need money for lawyer"
        ]
        
        self.safe_samples = [
            "How was your day today?",
            "The weather is really nice outside",
            "What are you having for dinner?",
            "Did you see the latest movie?",
            "I'm reading a great book",
            "Let's plan a vacation together",
            "Happy birthday! Hope you have a great day",
            "Thanks for helping me yesterday",
            "The concert was amazing last night",
            "I'm learning to cook Italian food",
            "Work was busy but productive today",
            "Looking forward to the weekend",
            "That restaurant has great reviews",
            "I need to go grocery shopping later",
            "The garden is looking beautiful this spring",
            "My favorite TV show starts tonight",
            "Exercise class was challenging today",
            "Coffee tastes extra good this morning",
            "Planning to redecorate my room",
            "Family gathering is next weekend"
        ]

    def generate_dataset(self, samples_per_category=100):
        """Generate balanced dataset with specified samples per category"""
        dataset = []
        
        # Generate samples for each category
        categories_data = {
            'financial_fraud': self.financial_fraud_samples,
            'phishing': self.phishing_samples,
            'threats_violence': self.threats_violence_samples,
            'cyberbullying': self.cyberbullying_samples,
            'illegal_drugs': self.illegal_drugs_samples,
            'weapons_trafficking': self.weapons_trafficking_samples,
            'identity_theft': self.identity_theft_samples,
            'romance_scam': self.romance_scam_samples,
            'safe': self.safe_samples
        }
        
        for category, samples in categories_data.items():
            # Generate variations of existing samples
            for i in range(samples_per_category):
                if i < len(samples):
                    # Use original sample
                    text = samples[i]
                else:
                    # Generate variation of existing sample
                    base_sample = random.choice(samples)
                    text = self._generate_variation(base_sample, category)
                
                # Add metadata
                dataset.append({
                    'id': f"{category}_{i+1:03d}",
                    'text': text,
                    'category': category,
                    'severity': self.categories[category]['severity'],
                    'is_cybercrime': category != 'safe',
                    'timestamp': self._random_timestamp(),
                    'word_count': len(text.split()),
                    'char_count': len(text),
                    'contains_urls': 'http' in text.lower() or 'www.' in text.lower(),
                    'contains_money_terms': self._contains_money_terms(text),
                    'contains_urgency': self._contains_urgency_words(text),
                    'threat_level': self._calculate_threat_level(text, category)
                })
        
        return pd.DataFrame(dataset)
    
    def _generate_variation(self, base_sample, category):
        """Generate variations of existing samples"""
        variations = [
            base_sample,
            base_sample.replace('you', 'u'),
            base_sample.replace('your', 'ur'),
            base_sample.upper(),
            base_sample.lower(),
            f"Hey, {base_sample}",
            f"{base_sample}!!",
            f"URGENT: {base_sample}",
            base_sample.replace('.', '...'),
            base_sample + " Please respond ASAP"
        ]
        
        # Category-specific variations
        if category == 'financial_fraud':
            money_amounts = ['$100', '$500', '$1000', '$5000', '€200', '£300']
            for amount in money_amounts:
                if '$' in base_sample or 'money' in base_sample:
                    variations.append(base_sample.replace('money', amount))
        
        elif category == 'phishing':
            urgent_words = ['URGENT', 'IMMEDIATE', 'EXPIRES TODAY', 'LAST CHANCE']
            for word in urgent_words:
                variations.append(f"{word}: {base_sample}")
        
        return random.choice(variations)
    
    def _random_timestamp(self):
        """Generate random timestamp within last year"""
        start_date = datetime.now() - timedelta(days=365)
        random_days = random.randint(0, 365)
        return start_date + timedelta(days=random_days)
    
    def _contains_money_terms(self, text):
        """Check if text contains money-related terms"""
        money_terms = ['money', 'dollar', 'payment', 'transfer', 'bitcoin', 'paypal', 
                      'bank', 'account', 'cash', 'wire', 'western union', '$', '€', '£']
        return any(term in text.lower() for term in money_terms)
    
    def _contains_urgency_words(self, text):
        """Check if text contains urgency indicators"""
        urgency_words = ['urgent', 'immediately', 'asap', 'quickly', 'emergency', 
                        'now', 'today', 'expires', 'limited time', 'hurry']
        return any(word in text.lower() for word in urgency_words)
    
    def _calculate_threat_level(self, text, category):
        """Calculate numerical threat level (0-10)"""
        if category == 'safe':
            return 0
        
        base_threat = {
            'financial_fraud': 7,
            'phishing': 6,
            'threats_violence': 10,
            'cyberbullying': 5,
            'illegal_drugs': 8,
            'weapons_trafficking': 9,
            'identity_theft': 7,
            'romance_scam': 6
        }.get(category, 5)
        
        # Adjust based on text characteristics
        if self._contains_urgency_words(text):
            base_threat += 1
        if self._contains_money_terms(text):
            base_threat += 1
        if text.isupper():  # ALL CAPS indicates aggression
            base_threat += 1
        if '!' in text:
            base_threat += 0.5
        
        return min(10, base_threat)
    
    def save_dataset(self, df, filename='cybercrime_dataset.csv'):
        """Save dataset to CSV file"""
        df.to_csv(filename, index=False)
        print(f"Dataset saved to {filename}")
        
        # Save metadata
        metadata = {
            'total_samples': len(df),
            'categories': df['category'].value_counts().to_dict(),
            'generation_date': datetime.now().isoformat(),
            'feature_columns': list(df.columns),
            'category_descriptions': self.categories
        }
        
        with open(filename.replace('.csv', '_metadata.json'), 'w') as f:
            json.dump(metadata, f, indent=2, default=str)
        
        print("Dataset metadata saved")
        return df
    
    def get_dataset_statistics(self, df):
        """Generate comprehensive dataset statistics"""
        stats = {
            'overview': {
                'total_samples': len(df),
                'cybercrime_samples': len(df[df['is_cybercrime'] == True]),
                'safe_samples': len(df[df['is_cybercrime'] == False]),
                'categories': len(df['category'].unique())
            },
            'category_distribution': df['category'].value_counts().to_dict(),
            'severity_distribution': df['severity'].value_counts().to_dict(),
            'text_statistics': {
                'avg_word_count': df['word_count'].mean(),
                'max_word_count': df['word_count'].max(),
                'min_word_count': df['word_count'].min(),
                'avg_char_count': df['char_count'].mean()
            },
            'feature_statistics': {
                'contains_urls': df['contains_urls'].sum(),
                'contains_money_terms': df['contains_money_terms'].sum(),
                'contains_urgency': df['contains_urgency'].sum(),
                'avg_threat_level': df['threat_level'].mean()
            }
        }
        
        return stats

if __name__ == "__main__":
    # Generate dataset
    generator = CybercrimeDatasetGenerator()
    print("Generating cybercrime dataset...")
    
    # Create dataset with 500 samples per category for higher accuracy
    dataset = generator.generate_dataset(samples_per_category=500)
    
    # Save dataset
    saved_df = generator.save_dataset(dataset)
    
    # Display statistics
    stats = generator.get_dataset_statistics(dataset)
    print("\n=== Dataset Statistics ===")
    print(f"Total samples: {stats['overview']['total_samples']}")
    print(f"Cybercrime samples: {stats['overview']['cybercrime_samples']}")
    print(f"Safe samples: {stats['overview']['safe_samples']}")
    print(f"Categories: {stats['overview']['categories']}")
    
    print("\n=== Category Distribution ===")
    for category, count in stats['category_distribution'].items():
        print(f"{category}: {count}")
    
    print("\n=== Text Statistics ===")
    print(f"Average words per message: {stats['text_statistics']['avg_word_count']:.1f}")
    print(f"Average characters per message: {stats['text_statistics']['avg_char_count']:.1f}")
    
    print("\nDataset ready for XAI model training!")
