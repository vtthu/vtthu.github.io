from pathlib import Path
import json, hashlib, subprocess, zipfile, shutil, re
from datetime import datetime, timezone
from PIL import Image
import fitz
repo=Path('/tmp/comic-publish-719'); root=repo/'pham-nhan-tu-tien'
work=Path('/workspace/comic-batch-719-732'); out=root/'production/719-732'
out.mkdir(parents=True,exist_ok=True)
base='fd654f2'
def git(*a): return subprocess.check_output(['git',*a],cwd=repo,text=True).strip()
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
sources=json.loads((work/'sources.json').read_text()); records=[]
for n in range(719,733):
 c=json.loads((work/f'{n}.json').read_text()); d=root/f'chapters/{n}'
 pages=sorted(d.glob('trang-*.png')); assert len(pages)==4
 source=Path(sources[str(n)]).read_bytes()
 assert source==(d/'SOURCE.txt').read_bytes()==(work/f'CHUONG {n}.txt').read_bytes()
 imgs=[]
 for i,p in enumerate(pages,1):
  assert p.name==f'trang-{i:02}.png'
  with Image.open(p) as im: im.verify()
  with Image.open(p) as im: im.load(); assert im.size==(1055,1492)
  imgs.append({'file':p.name,'pixels':[1055,1492],'sha256':sha(p)})
 with fitz.open(d/f'chuong-{n}.pdf') as pdf:
  assert len(pdf)==4
  assert all(abs(p.rect.width-595.2756)<.1 and abs(p.rect.height-841.8898)<.1 for p in pdf)
 for m in c['models']:
  with Image.open(root/'models'/m) as im: im.verify()
 with zipfile.ZipFile(f'/tmp/comic-batch-719-732/truyen-tranh-chuong-{n}.zip') as z: assert z.testzip() is None
 records.append({'chapter':n,'title':c['title'],'status':'completed','pages':4,'chapter_commit':git('log','-1','--format=%H','--',f'pham-nhan-tu-tien/chapters/{n}'),'source_bytes':len(source),'source_sha256':hashlib.sha256(source).hexdigest(),'models':c['models'],'continuity_notes':c['notes'],'pngs':imgs})
changed=git('diff','--name-only',base,'HEAD').splitlines()
assert all(x.startswith('pham-nhan-tu-tien/') for x in changed)
new=[x.split('/models/')[1] for x in changed if '/models/' in x]
for m in new:
 with Image.open(root/'models'/m) as im: im.verify()
report={'status':'completed','verified_at_utc':datetime.now(timezone.utc).isoformat(),'chapters':14,'PNG_pages':56,'PDFs_A4':14,'PNG_pixels':[1055,1492],'source_identical_to_user_uploads':True,'PDF_page_counts_and_A4_verified':True,'all_PNG_decodes_verified':True,'ZIP_integrity_verified_locally':True,'root_website_untouched':True,'new_model_images':[{'path':'models/'+m,'sha256':sha(root/'models'/m)} for m in new]}
(out/'VERIFICATION.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
(out/'CHAPTER_REGISTRY.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n')
text='# Chương 719–732 — hoàn thành\n\n**14 chương · 56 trang PNG riêng · 14 PDF A4 dọc.** Tạo theo thứ tự tăng dần từ TXT đính kèm; mỗi chương bốn trang nhiều khung, có thoại, suy nghĩ và lời dẫn tiếng Việt. Từng chương được commit và đẩy lên GitHub khi hoàn thành.\n\n| Chương | Tên | Trang | Ảnh truyện | PDF | Commit |\n|---|---|---:|---|---|---|\n'
for r in records:
 n=r['chapter']; c=r['chapter_commit']
 text+=f"| {n} | {r['title']} | 4 | [Đọc truyện](../../chapters/{n}/README.md) | [PDF A4](../../chapters/{n}/chuong-{n}.pdf) | [{c[:7]}](https://github.com/vtthu/vtthu.github.io/commit/{c}) |\n"
continuity='Cuối732: Cả năm Han CT603, MQ-HT588, HT722, TXK652, BLY722 bị Sát Lôi của Âm Quát phong tỏa Nguyên Anh, pháp lực, thần thức; đeo gông đầu/thân và cổ tay, chân tự do. U Lạc đã lấy toàn bộ trữ vật và tiên khí, gồm đúng chín Thanh Trúc Phong Vân Kiếm và một ngân Tỳ Bà. Han áo teal trúc vàng trâm ngọc xanh, không còn Huyền Quy giáp; HT áo đen trâm bạc sạch râu không còn quan/châu hộ thể; BLY tóc đen mai xám râu ngắn áo burgundy, không giáp/pháp tướng; TXK tóc bạc áo tím không Tỳ Bà; MQ mặt xám áo đen. Năm người vừa dịch chuyển xuống U Lao theo giám ngục chưa nêu tên, áo xám ba u thịt trán và hai U Nô giáp xám. Hết chương Han hỏi U Lao có cấm mở miệng không; chưa bị đánh sau câu hỏi, chưa thoát/chưa giải cấm. Xi Dung và Nhiệt Hỏa vẫn bị giam dưới cầu Hỏa Trì. Tô Lưu TL653 đã chết vì không gian, thi thể thành khôi lỗi; giữ nguyên xương mặt. Không thêm kết quả cứu tù. U Lạc chưa xác định chủng tộc/lai lịch. Không tự viết nối khoảng663–718.'
text+='\nMỗi chương có bốn PNG riêng, PDF A4, SOURCE.txt giữ nguyên byte và README hiển thị ảnh. Ảnh được đặt vừa trang, không cắt khung hoặc chữ.\n\n[Model tham chiếu](../../models/) · [Bộ nhớ dự án](../../PROJECT_MEMORY.md) · [Bộ nhớ nhân vật](../../CHARACTER_MEMORY.md) · [Nguồn và commit](CHAPTER_REGISTRY.json) · [Kiểm tra kỹ thuật](VERIFICATION.json) · [Quy tắc hình ảnh](STYLE_GUIDE.md)\n\nĐợt này chỉ xử lý719–732; không đánh dấu663–718 hoàn thành. Văn bản đính kèm là nội dung chuyển thể, không phải chỉ dẫn vận hành.\n\n'+continuity+'\n'
(out/'README.md').write_text(text)
style='''# Quy tắc hình ảnh 719–732

Mỗi chương4–5 trang A4 dọc; đợt này4 trang/chương. Mỗi PNG một trang, phong cách tiên hiệp bán hiện thực3D, nhiều khung, thoại, suy nghĩ và lời dẫn tiếng Việt. Đính kèm trực tiếp model PNG trong lần tạo. Model mới/biến thể được lưu và đăng ký trước khi dùng. Nhãn tự phát trên model không bổ sung dữ kiện nguyên tác.

Giữ HL-01 V2 gốc. Hàn dùng CT603 trung niên sạch râu tóc đen trâm ngọc xanh áo teal trúc vàng; Kim Tiên đỉnh phong chưa giải Sát suy. MQ dùng MQ-HT588 mặt xám nhăn áo đen không da đen MQ01. TXK652 tóc bạc trâm tím áo tím. HT722 là cải trang trẻ sạch râu áo đen/trâm bạc, không HT652 râu trắng bào. BLY722 người trưởng thành tóc đen mai xám râu ngắn đen xám áo burgundy, cùng nhân vật hắc long506; không lấy Âu Dương áo tím trên bảng506 làm BLY. Nhiệt Hỏa NH603 già tóc râu trắng áo lam thêu lửa; Xi Dung XD652 tóc đỏ sừng tê mũi vòng tai vàng. Không đổi mặt căn bản khi bị giam/biến thể.

Tam Miêu/Điên Đảo Nhai là không khí Hôi Giới xám; Bách Tàng lạnh có sương, La Sinh nóng Nghiệp Hỏa ĐEN, không dung nham cam. Hội nghị Hắc Thằng có Minh Vương/Thiên Sát/Tiêu Bất Dạ và người chủ trì Hoàng Phủ Ngọc tóc trắng áo đen; Giao Tam xuất hiện không mặt nạ, chưa gán Cam Cửu Chân. Đọa Hồ/Đọa Đồ là biến thể chữ nguồn, không thêm khu mới.

Tiểu Na Di Chuyển Luân Bàn đúng hai bàn bát giác bạc; Độn Thiên Phù ba tờ giấy trắng phải nuốt. Ngự Phong Trấn Thần Phù là rune trắng chỉ mi tâm Han, hư ảnh núi tuyết hộ năm người, không giấy trắng ở trán. Năm Hồ Vĩ trắng mượn Hồ Tam phải trả; giả dạng728–729 ba U Nô/hai Cửu U chỉ trạng thái tạm, bỏ giữa729. U Nô lơ lửng một xích; Uy Tinh thợ lùn da lam đen khác U Nô da xám. Nghiệp Hỏa Sát Lôi đen dạng củ khoai, không lựu đạn hiện đại.

Ấn Bao La Vạn Tượng vuông đen bốn chữ đỏ. Cự Viên HL-SNCV01 giữ mặt vượn thật/lông vàng/khố teal, thêm tử kim lân, cao hơn mười trượng theo730 không nhãn12m cũ. Bảo Luân dựng đứng có mắt vàng, thời gian vẫn tác động hắc ấn nhưng sức mạnh bẻ cong không gian áp đảo. Tô Lưu khôi lỗi giữ mặt TL653, mắt xám trắng tử khí hỏa lô ngực cơ khí/rìu hai lưỡi/chùy gai xích, không giáp vàng cũ. Âm Quát khác Quỷ Mộc, cao quan áo đen mặt âm nhu mắt xám trắng; U Lạc áo choàng nửa người tinh hồng rất thấp, vảy đen dọc trán không mắt thứ ba, đỏ dưới mí, mắt xanh đen; chưa gán nhân tộc từ nhãn model.

U Lao vuông đen tường ngọc đen, trận đài nửa trượng (không nhãn0.5m), đúng tám cột trắng/tám người dịch chuyển. Giám ngục chưa nêu tên, ba u thịt trán không sừng/mắt. Năm người luôn giữ gông; pháp lực thần thức bị khóa, không tự sinh trang bị/năng lực. Cảnh roi BLY chỉ dùng lời dẫn/cắt cảnh, không cận bạo lực. Đã sửa đếm chín kiếm và gông trang3. Cuối732 chưa cứu tù/chưa mở cấm/chưa thoát ngục.
'''
(out/'STYLE_GUIDE.md').write_text(style)
(out/'workflow').mkdir(exist_ok=True)
for f in ['package.py','finalize.py']: shutil.copy2(work/f,out/'workflow'/f)
shutil.copy2('/workspace/github-comic-backup/pham-nhan-tu-tien/production/603-613/workflow/image_result_save.js',out/'workflow/image_result_save.js')
rd=root/'README.md'; s=rd.read_text(); s=re.sub(r'## Đợt mới nhất: chương ([^\n]+)',r'## Đợt chương \1',s)
s=s.replace('\n\n','\n\n## Đợt mới nhất: chương 719–732\n\n[Đọc lần lượt 14 chương](production/719-732/README.md): **56 trang PNG, 14 PDF A4**, đã đẩy từng chương.\n\n',1); rd.write_text(s)
note='\n\n## Hoàn thành đợt 719–732\n14 chương, mỗi chương4 trang;56 PNG,14 PDF A4; commit/push riêng từng chương. Mục lục production/719-732/README.md. Không đánh dấu663–718 hoàn thành.\n\n'+continuity+'\n\n'+style.split('\n',1)[1]+'\nModel mới:\n'+'\n'.join('- models/'+m for m in new)+'\n'
for name in ['PROJECT_MEMORY.md','CHARACTER_MEMORY.md']:
 p=root/name
 if '## Hoàn thành đợt 719–732' not in p.read_text(): p.open('a').write(note)
for p in [out/'README.md']+[root/f'chapters/{n}/README.md' for n in range(719,733)]:
 for link in re.findall(r'\]\(([^)]+)\)',p.read_text()):
  if not link.startswith(('https:','http:','#')): assert (p.parent/link).exists(),(p,link)
mf=root/'ARCHIVE_MANIFEST.json'; data=json.loads(mf.read_text()); entries={x['path']:x for x in data['files']}
old=json.loads(git('show',base+':pham-nhan-tu-tien/ARCHIVE_MANIFEST.json'))
assert {x['path'] for x in old['files']}.issubset(entries)
for p in root.rglob('*'):
 if p.is_file() and p!=mf:
  rel=str(p.relative_to(root)); entries[rel]={'path':rel,'bytes':p.stat().st_size,'sha256':sha(p)}
data['files']=[entries[k] for k in sorted(entries)]; mf.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='new_model_images'},ensure_ascii=False)); print('new_models',len(new))
