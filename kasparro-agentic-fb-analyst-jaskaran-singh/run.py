import json
import os
import pandas as pd
from datetime import datetime
from typing import Dict, List, Any
import re

# This is data file location 
DATA_FILE_LOCATION = r"C:\Desktop\kasparro-agentic-fb-analyst-jaskaran-singh\synthetic_fb_ads_undergarments.csv"

class TaskOrganizer:
    def create_plan(self, user_request: str) -> Dict:
        print(" Planning out the analysis steps...")
        steps_to_follow = [
            "Get the Facebook Ads data ready",
            "Look for ROAS patterns and drops", 
            "Come up with ideas about what might be wrong",
            "Check if those ideas make sense with the numbers",
            "Brainstorm better ad ideas for struggling campaigns"
        ]
        for step in steps_to_follow:
            print(f"   Ready for: {step}")
        return {"user_request": user_request, "steps": steps_to_follow}

class DataHandler:
    def get_data(self) -> pd.DataFrame:
        print(" Working with the data file...")
        try:
            data_frame = pd.read_csv(DATA_FILE_LOCATION)
            print(f"    Found {len(data_frame)} records with {len(data_frame.columns)} data points")
            print(f"    Using file from: {DATA_FILE_LOCATION}")
            
            data_frame['date'] = pd.to_datetime(data_frame['date'], dayfirst=True, errors='coerce')
            data_frame = data_frame.dropna(subset=['date']).sort_values('date')
            print(f"   Data covers: {data_frame['date'].min().strftime('%Y-%m-%d')} to {data_frame['date'].max().strftime('%Y-%m-%d')}")
            return data_frame
        except Exception as error:
            print(f"    Problem loading data: {error}")
            return None
    
    def examine_patterns(self, data_frame: pd.DataFrame) -> Dict:
        print(" Looking at ROAS trends...")
        
        weekly_data = data_frame.groupby(pd.Grouper(key='date', freq='W')).agg({
            'roas': 'mean', 'spend': 'sum', 'ctr': 'mean'
        }).reset_index()
        
        weekly_data['roas_change'] = weekly_data['roas'].pct_change()
        bad_periods = weekly_data[weekly_data['roas_change'] < -0.2]
        
        print(f"    Found {len(bad_periods)} periods where ROAS dropped significantly")
        return {
            "campaign_count": data_frame['campaign_name'].nunique(),
            "average_roas": float(data_frame['roas'].mean()),
            "average_ctr": float(data_frame['ctr'].mean()),
            "drop_count": len(bad_periods)
        }

class IdeaGenerator:
    def come_up_with_theories(self, data_frame: pd.DataFrame) -> List[Dict]:
        print(" Thinking about what might be happening...")
        theories = []
        
        campaign_numbers = data_frame.groupby('campaign_name').agg({
            'roas': 'mean', 'spend': 'sum', 'ctr': 'mean'
        })
        big_spenders_low_results = campaign_numbers[
            (campaign_numbers['spend'] > campaign_numbers['spend'].median()) &
            (campaign_numbers['roas'] < campaign_numbers['roas'].median())
        ]
        if not big_spenders_low_results.empty:
            theories.append({
                "theory_type": "ad_fatigue",
                "name": "Ads Getting Tired in Big Budget Campaigns",
                "explanation": "Campaigns spending a lot but not getting good returns",
                "certainty": 0.75,
                "proof": {
                    "problem_campaigns": big_spenders_low_results.index.tolist()[:3],
                    "average_roas": float(big_spenders_low_results['roas'].mean()),
                    "total_money_spent": float(big_spenders_low_results['spend'].sum())
                }
            })
        
        if 'audience_type' in data_frame.columns:
            audience_results = data_frame.groupby('audience_type')['roas'].mean()
            poor_performers = audience_results[audience_results < audience_results.median()]
            if not poor_performers.empty:
                theories.append({
                    "theory_type": "audience_burnout", 
                    "name": "Audience Getting Tired",
                    "explanation": "Some audience groups not responding well anymore",
                    "certainty": 0.65,
                    "proof": {
                        "tired_audiences": poor_performers.index.tolist(),
                        "performance_difference": float(audience_results.max() - audience_results.min())
                    }
                })
        
        low_engagement_campaigns = data_frame.groupby('campaign_name')['ctr'].mean().nsmallest(3)
        if not low_engagement_campaigns.empty:
            theories.append({
                "theory_type": "poor_engagement",
                "name": "Low Click-Through Campaigns", 
                "explanation": "Campaigns where people aren't clicking much",
                "certainty": 0.60,
                "proof": {
                    "low_ctr_campaigns": low_engagement_campaigns.index.tolist(),
                    "average_ctr": float(low_engagement_campaigns.mean())
                }
            })
        
        for theory in theories:
            print(f"    {theory['name']} (Certainty: {theory['certainty']})")
        return theories

class TheoryChecker:
    def check_theories(self, data_frame: pd.DataFrame, theories: List[Dict]) -> List[Dict]:
        print(" Testing our theories with actual numbers...")
        for theory in theories:
            if theory['theory_type'] == 'ad_fatigue':
                campaigns = theory['proof']['problem_campaigns']
                going_down = 0
                for campaign in campaigns[:2]:
                    campaign_info = data_frame[data_frame['campaign_name'] == campaign].sort_values('date')
                    if len(campaign_info) > 1:
                        direction = (campaign_info['roas'].iloc[-1] - campaign_info['roas'].iloc[0]) / campaign_info['roas'].iloc[0]
                        if direction < -0.1:
                            going_down += 1
                certainty = 0.5 + (going_down / len(campaigns[:2])) * 0.3 if campaigns else 0.3
            else:
                certainty = 0.6 
            theory['checked_certainty'] = float(certainty)
            theory['makes_sense'] = bool(certainty >= 0.6)
            result = " MAKES SENSE" if theory['makes_sense'] else "❌ DOESN'T HOLD UP"
            print(f"   {result} {theory['name']} (Certainty: {certainty:.2f})")
        
        return theories

class AdIdeaCreator:
    def create_better_ads(self, data_frame: pd.DataFrame, theories: List[Dict]) -> Dict:
        print(" Creating fresh ad ideas...")
        
        best_performers = data_frame.nlargest(10, 'roas')
        best_ad_texts = best_performers['creative_message'].dropna().tolist()
        
        good_ctas = self._find_good_ctas(best_ad_texts)
        good_themes = self._find_popular_themes(best_ad_texts)
        
        struggling_campaigns = data_frame.groupby('campaign_name')['ctr'].mean().nsmallest(3)
        campaign_suggestions = []
        
        for campaign, current_ctr in struggling_campaigns.items():
            new_ideas = self._make_campaign_ideas(campaign, current_ctr, good_themes, good_ctas)
            campaign_suggestions.append({
                "campaign_name": campaign,
                "current_ctr_score": float(current_ctr),
                "new_ad_options": new_ideas
            })
            print(f"   Made {len(new_ideas)} new ideas for {campaign}")
        
        return {
            "learned_from_best": {
                "effective_ctas": good_ctas,
                "popular_themes": good_themes
            },
            "campaign_improvements": campaign_suggestions,
            "things_to_try": [
                "Test new call-to-actions against current ones",
                "Try time-limited offers and urgency",
                "Experiment with different ad layouts"
            ]
        }
    
    def _find_good_ctas(self, messages: List[str]) -> List[str]:
        ctas_found = []
        for message in messages:
            found_words = re.findall(r'(buy now|shop now|order now|discover|learn more|sign up)', message.lower())
            ctas_found.extend(found_words)
        return list(set(ctas_found))[:5]
    
    def _find_popular_themes(self, messages: List[str]) -> List[str]:
        common_themes = []
        theme_words = {
            'comfort': ['comfort', 'soft', 'smooth', 'comfortable'],
            'quality': ['premium', 'quality', 'durable', 'best'],
            'value': ['sale', 'deal', 'offer', 'discount', 'save'],
            'urgency': ['limited', 'today', 'now', 'while supplies']
        }
        for theme, words in theme_words.items():
            matches = sum(1 for msg in messages if any(word in msg.lower() for word in words))
            if matches > len(messages) * 0.2:
                common_themes.append(theme)
        return common_themes
    
    def _make_campaign_ideas(self, campaign: str, ctr: float, themes: List[str], ctas: List[str]) -> List[str]:
        ideas_list = []
        possible_ideas = [
            f"Experience amazing {themes[0] if themes else 'comfort'}. {ctas[0].title() if ctas else 'Shop Now'}!",
            f"Special {themes[1] if len(themes) > 1 else 'limited-time'} offer. {ctas[1].title() if len(ctas) > 1 else 'Buy Today'}!",
            f"Find your perfect {themes[0] if themes else 'fit'} for daily wear. {ctas[0].title() if ctas else 'Order Now'}!",
            f"Top-notch {themes[0] if themes else 'quality'} you'll enjoy. {ctas[0].title() if ctas else 'Shop Today'}!",
            f"Check out our {themes[1] if len(themes) > 1 else 'new'} collection. {ctas[1].title() if len(ctas) > 1 else 'Discover More'}!"
        ]
        return possible_ideas[:4]

class AdsAnalysisTool:
    def __init__(self):
        self.organizer = TaskOrganizer()
        self.data_manager = DataHandler()
        self.idea_maker = IdeaGenerator()
        self.theory_tester = TheoryChecker()
        self.ad_creator = AdIdeaCreator()
    
    def run_analysis(self, user_question: str):
        print("Starting Facebook Ads Analysis...")
        print("=" * 60)
        
        try:
            self.organizer.create_plan(user_question)
            
            data = self.data_manager.get_data()
            if data is None:
                print(" Can't continue without data")
                return
            
            trends_found = self.data_manager.examine_patterns(data)
            
            theories = self.idea_maker.come_up_with_theories(data)
            
            checked_theories = self.theory_tester.check_theories(data, theories)
            
            new_ad_ideas = self.ad_creator.create_better_ads(data, checked_theories)
            
            self._create_results(data, checked_theories, new_ad_ideas, trends_found)
            
            print("\n" + "=" * 60)
            print(" Analysis Finished Successfully!")
            print(f"{trends_found['campaign_count']} campaigns reviewed")
            print(f" {len([t for t in checked_theories if t['makes_sense']])} theories that make sense")
            print(f" {len(new_ad_ideas['campaign_improvements'])} sets of ad ideas created")
            
        except Exception as error:
            print(f" Something went wrong: {error}")
            import traceback
            traceback.print_exc()
    
    def _create_results(self, data_frame: pd.DataFrame, theories: List[Dict], ad_ideas: Dict, trends: Dict):
        os.makedirs('logs', exist_ok=True)
        
        analysis_results = {
            "when_analyzed": datetime.now().isoformat(),
            "overall_numbers": {
                "campaigns_looked_at": trends['campaign_count'],
                "average_roas_score": trends['average_roas'],
                "average_ctr_score": trends['average_ctr'],
                "bad_periods_count": trends['drop_count']
            },
            "theories_checked": [{
                "theory_name": t["name"],
                "theory_explanation": t["explanation"], 
                "confidence_level": t["checked_certainty"],
                "theory_holds_up": t["makes_sense"],
                "supporting_evidence": t["proof"]
            } for t in theories]
        }
        
        with open('insights.json', 'w') as output_file:
            json.dump(analysis_results, output_file, indent=2)
        print("   insights.json created")
        
        with open('creatives.json', 'w') as output_file:
            json.dump(ad_ideas, output_file, indent=2)
        print("   creatives.json created")
        
        good_theories = [t for t in theories if t['makes_sense']]
        report_content = f"""# Facebook Ads Analysis Results

## What We Found
We looked at {trends['campaign_count']} campaigns and found {len(good_theories)} main issues affecting performance.

## The Numbers
- **Campaigns Reviewed**: {trends['campaign_count']}
- **Average ROAS**: {trends['average_roas']:.2f}
- **Average CTR**: {trends['average_ctr']:.3f}%
- **Problem Periods**: {trends['drop_count']}

## Our Conclusions
"""
        
        for theory in good_theories:
            report_content += f"### {theory['name']}\n"
            report_content += f"- **Confidence**: {theory['checked_certainty']:.2f}\n"
            report_content += f"- **What This Means**: {theory['explanation']}\n"
            report_content += f"- **Why We Think This**: {json.dumps(theory['proof'], indent=2)}\n\n"
        
        report_content += "## Suggested Ad Improvements\n\n"
        report_content += "### What's Working Well\n"
        report_content += f"- **Good CTAs**: {', '.join(ad_ideas['learned_from_best']['effective_ctas'])}\n"
        report_content += f"- **Popular Themes**: {', '.join(ad_ideas['learned_from_best']['popular_themes'])}\n\n"
        
        report_content += "### Campaign-Specific Suggestions\n"
        for campaign in ad_ideas['campaign_improvements']:
            report_content += f"#### {campaign['campaign_name']} (Current CTR: {campaign['current_ctr_score']:.3f}%)\n"
            for idea in campaign['new_ad_options']:
                report_content += f"- {idea}\n"
            report_content += "\n"
        
        report_content += "### Testing Ideas\n"
        for suggestion in ad_ideas['things_to_try']:
            report_content += f"- {suggestion}\n"
        
        report_content += f"\n---\n*Created on {datetime.now().strftime('%Y-%m-%d %H:%M')}*"
        
        with open('report.md', 'w', encoding='utf-8') as report_file:
            report_file.write(report_content)
        print("   report.md created")

if __name__ == "__main__":
    import sys
    user_input = sys.argv[1] if len(sys.argv) > 1 else "Look at ROAS drops and suggest better ads"
    analysis_tool = AdsAnalysisTool()
    analysis_tool.run_analysis(user_input)